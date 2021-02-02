import re
from functools import partial

import openai
import os
import random
from multiprocessing.pool import ThreadPool
from create_html import google_search_html, wikipedia_html
from tokenizer import logit_mask, tokenize
from conditional import counterfactual
from masks import *

openai.api_key = os.environ["OPENAI_API_KEY"]

def split_prompt_template(prompt, start_delimiter='{', end_delimiter='}'):
    parts = re.split(rf"{start_delimiter}", prompt)
    prompt_sections = []
    blanks = []
    prompt_sections.append(parts[0])
    for i, part in enumerate(parts[1:]):
        section = re.split(rf"{end_delimiter}", part)
        blanks.append(section[0])
        prompt_sections.append(section[1])

    return prompt_sections, blanks


def api_call(prompt, engine="curie", n=1, temperature=0.8, max_tokens=100, logprobs=0, stop='default', mask=None):
    if mask is None:
        mask = {}
    if stop == 'default':
        stop = ["\""]
    return openai.Completion.create(
        engine=engine,
        prompt=prompt,
        temperature=temperature,
        max_tokens=max_tokens,
        echo=False,
        top_p=1,
        n=n,
        stop=stop,
        timeout=15,
        logprobs=logprobs,
        logit_bias=mask
    )


#TODO logit bias for websites
def query_google(search_query, engine="curie", num_results=1):
    with open("alternet/prompts/google_prompt_1.txt") as f:
        prompt = f.read()
    search_results = {}
    prompt_sections, blanks = split_prompt_template(prompt=prompt)
    prompt1 = prompt_sections[0] + search_query + prompt_sections[1]
    response1 = api_call(prompt=prompt1, engine=engine)
    search_results['title'] = response1.choices[0]["text"]
    prompt2 = prompt1 + search_results['title'] + prompt_sections[2]
    response2 = api_call(prompt=prompt2, engine=engine)
    search_results['domain'] = response2.choices[0]["text"]
    prompt3 = prompt2 + search_results['domain'] + prompt_sections[3] + search_results['domain']
    response3 = api_call(prompt=prompt3, engine=engine)
    search_results['url'] = response3.choices[0]["text"]
    prompt4 = prompt3 + search_results['url'] + prompt_sections[4]
    response4 = api_call(prompt=prompt4, engine=engine)
    search_results['preview'] = response4.choices[0]["text"]
    random_month = random.choice(['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                                  'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'])
    random_day = random.randint(1, 30)
    prompt5 = prompt4 + search_results['preview'] + prompt_sections[5] + ' ' + \
              random_month + ' ' + str(random_day) + ','

    response5 = api_call(prompt=prompt5, engine=engine, stop=[".", "\n", ","])
    year = response5.choices[0]["text"]
    search_results['date'] = random_month + ' ' + str(random_day) + ',' + year

    return search_results


def create_google_search_page(query, n=3, engine='curie', filename='auto'):
    # search_results = []
    if filename == 'auto':
        filename = f'alternet/googpt/query={query}_model={engine}.html'
    pool = ThreadPool(n)
    search_results = pool.map(partial(query_google, engine=engine), [query] * n)
    # for i in range(n):
    #     search_results.append(search_google(query, engine="davinci", num_results=1))

    html = google_search_html(query, search_results)
    html_file = open(filename, "w")
    html_file.write(html)
    html_file.close()


def extract_section_text(response, prompt, stop_sequence='\"'):
    text = response.choices[0]["text"]
    if response.choices[0]["finish_reason"] == "length":
        counterfactuals_n = counterfactual(response, stop_sequence, next_token='\n', sort=True)
        if len(counterfactuals_n) == 0:
            print('no counterfactuals')
            section_text = text.splitlines()[0]
        else:
            section_text = text[:counterfactuals_n[-1]['position'] - len(prompt)]
    else:
        section_text = text
    return section_text


# TODO don't force title to come first, but bold first instance of title...
def generate_wiki_intro(content, engine):
    prompt = f'''I click on the link "en.wikipedia.org/wiki/{content['url']}" and the Wikipedia page for {content['title']} loads in my browser. 
    The article introduction reads:
    "{content['title']} From Wikipedia, the free encyclopedia {content['title']}'''
    prompt2 = f'''I click on the link "en.wikipedia.org/wiki/{content['url']}" and the Wikipedia page for {content['title']} loads in my browser. 
    The article introduction reads:
    "{content['title']} From Wikipedia, the free encyclopedia The {content['title']}'''
    # prompt = prompt2

    content['title_token'] = tokenize(content['title'])[0]
    anti_repetition_mask = {content['title_token']: -100,
                            t_NEWLINE: -100,
                            t_From: -100,
                            t_is: 50,
                            t_was: 50,
                            t_are: 50,
                            t_oparen: 40}
    # anti_repetition_mask = logit_mask(anti_repetition_mask)
    response = api_call(prompt=prompt, engine=engine, max_tokens=1, mask=anti_repetition_mask, temperature=0.6)
    first_token = response.choices[0]["text"]
    prompt += (' ' + first_token)
    response = api_call(prompt=prompt, engine=engine, max_tokens=400, temperature=0.8,
                        stop=["\"\n", "\" \n"],
                        logprobs=100)

    introduction = extract_section_text(response, prompt, stop_sequence='\"')

    content['introduction'] = ' ' + first_token + introduction

    return prompt + content['introduction']


def generate_TOC(content, prompt_after_intro, engine='curie'):
    toc_prompt_frag = f'''" 
    The table of contents reads:
    "Contents
    1'''

    toc_prompt = prompt_after_intro + toc_prompt_frag
    first_token_mask = TOC_first_token_mask
    first_token_mask[content['title_token']]: -90
    response = api_call(prompt=toc_prompt, engine=engine, max_tokens=1, temperature=0.7, mask=first_token_mask,
                        stop=["\n", "\""])
    TOC_first_token = response.choices[0]["text"]
    TOC_firstline_prompt = toc_prompt + TOC_first_token
    response = api_call(prompt=TOC_firstline_prompt, engine=engine, max_tokens=5, temperature=0.7, stop=["\"", "\n"],
                        mask=TOC_first_line_mask)
    TOC_firstline = response.choices[0]["text"]

    TOC_secondline_prompt = TOC_firstline_prompt + TOC_firstline + '\n'
    response = api_call(prompt=TOC_secondline_prompt, engine=engine, max_tokens=1, temperature=0.7, stop=["\"", "\n"],
                        mask=TOC_secondline_mask)
    TOC_second_number = response.choices[0]["text"]

    response = api_call(prompt=TOC_secondline_prompt + TOC_second_number, engine=engine, max_tokens=300,
                        temperature=0.7, stop=["\"", "\n\n"],
                        mask=TOC_rest_mask)
    TOC_rest = response.choices[0]["text"]

    content["TOC_plaintext"] = '1' + TOC_first_token + TOC_firstline + '\n' + TOC_second_number + TOC_rest
    process_TOC_plaintext(content)
    print(content["TOC_plaintext"])
    if len(content["flattened_TOC"]) > 25:
        print('long TOC...')
        exit(0)
    #toc_items = content["TOC_plaintext"].splitlines()
    content["TOC"] = {}
    content["TOC"]["children"] = []
    content["TOC_index"] = 0
    TOC_entry(parent=content["TOC"], content=content)

    # print('\n\n')
    #print(content["TOC"])


def process_TOC_plaintext(content):
    content['flattened_TOC'] = []
    fixed_TOC_plaintext = ''
    for i, line in enumerate(content["TOC_plaintext"].splitlines()):
        line_text = line.strip()

        try:
            number = line_text.split(" ")[0]
            if not number[0].isdigit():
                print('not digit')
                break
            content['flattened_TOC'].append({'line_text': line_text})
            content['flattened_TOC'][i]['number'] = number
            content['flattened_TOC'][i]['title'] = ' '.join(line_text.split(' ')[1:])

        except IndexError:
            print('index error trying to split entry')
            break
        fixed_TOC_plaintext += content['flattened_TOC'][i]['line_text'] + '\n'
        if content['flattened_TOC'][i]['title'] == 'References':
            break
    content["TOC_plaintext"] = fixed_TOC_plaintext


# TODO clean up
def TOC_entry(parent, content):
    if content["TOC_index"] == len(content['flattened_TOC']):
        return 'END'

    next_node_type = None

    return_msg = None
    while next_node_type != 'endOfList' and return_msg != 'END':

        try:
            next_node_type = lookahead(content['flattened_TOC'], content["TOC_index"])
            number = content['flattened_TOC'][content["TOC_index"]]["number"]
            title = content['flattened_TOC'][content["TOC_index"]]["title"]
        except IndexError:
            print('index error in TOC_entry while loop')
            return

        current_node = {'title': title,
                        'number': number}
        parent['children'].append(current_node)
        content["TOC_index"] += 1

        if next_node_type == 'child':
            if 'children' not in current_node:
                current_node["children"] = []
            return_msg = TOC_entry(parent=current_node, content=content)
        elif next_node_type == 'pop':
            return 'pop'
        else:
            # sibling
            pass

    try:
        number = content['flattened_TOC'][content["TOC_index"]]["number"]
        title = content['flattened_TOC'][content["TOC_index"]]["title"]

        current_node = {'title': title,
                        'number': number}
        parent['children'].append(current_node)
    except IndexError:
        print('index error in TOC_entry')
        return


def lookahead(items, index):
    #print(items[index])
    if index + 1 == len(items):
        #print('lookahead eol 1')
        return 'endOfList'
    try:
        current_num = items[index]["number"]
        #print('next: ', items[index+1])
        next_num = items[index+1]["number"]
    except IndexError:
        #print('index error splitting num in lookahead')
        return 'endOfList'
    if len(current_num) == len(next_num):
        return 'sibling'
    elif len(current_num) < len(next_num):
        return 'child'
    elif len(next_num) == 0:
        #print('lookahead eol 2')
        return 'endOfList'
    else:
        return 'pop'


# TODO always keep TOC in context window
# TODO error / try again if empty or generate multiple?
def generate_section(node, content, engine, toc=True):
    for i, child in enumerate(node["children"]):
        content['sections_text'] += '\n\n'
        stop = ["\n\n"]
        if toc:
            content['sections_text'] += child['number'] + ' '
            # TODO get next title from flat list instead
            if i + 1 < len(node['children']):
                stop.append(node['children'][i+1]['title'])
                stop.append(node['children'][i+1]['number'] + ' ' + node['children'][i+1]['title'])
                stop.append(node['children'][i+1]['number'] + node['children'][i+1]['title'])

        content['sections_text'] += child['title'] + '\n'

        intro_and_TOC = content['title'] + content['introduction'] + content['TOC_plaintext']
        if len(intro_and_TOC + content['sections_text']) > 6000:
            sections_window = content['sections_text'][-(6000-len(intro_and_TOC)):]
        else:
            sections_window = content['sections_text']
        prompt = intro_and_TOC + sections_window
        #print('prompt: ', prompt)
        response = api_call(prompt=prompt, engine=engine, max_tokens=1,
                            temperature=0.8, mask=section_begin_mask)
        first_token = response.choices[0]["text"]
        response = api_call(prompt=prompt + first_token, engine=engine, max_tokens=500,
                            temperature=0.8, stop=stop, logprobs=100)
        child['text'] = first_token + response.choices[0]["text"]
        #print('article text: {' + content['article_text'][-4000:] + '}')
        #print('section text: {' + child['text'] + '}')
        content['sections_text'] += child['text']
        if 'children' in child:
            generate_section(child, content, engine, toc)


def generate_sections(content, prompt_after_intro, engine, toc=True):
    # content['article_text'] = prompt_after_intro
    # if toc:
    #     content['article_text'] += content["TOC_plaintext"]
    content['sections_text'] = ''
    generate_section(content["TOC"], content, engine, toc)


# TODO use fewshot?
def generate_categories(content, prompt_after_intro, engine):

    categories_prompt_frag = f'''" 
    The article belongs to the following Categories: "'''

    # categories_prompt = prompt_after_intro + categories_prompt_frag
    # response = api_call(prompt=categories_prompt, engine=engine, max_tokens=50, temperature=0.7,
    #                     stop=["\""])
    # categories = response.choices[0]["text"]
    # print(categories_prompt)
    # print(categories)
    pass


def generate_infobox(content, prompt_after_intro, engine):
    pass


# TODO threading
def generate_wiki_article(content, engine='curie', TOC='True', sections='False', start_text=None, infobox=False):

    prompt_after_intro = generate_wiki_intro(content, engine)

    if TOC:
        generate_TOC(content, prompt_after_intro, engine)
        if sections:
            generate_sections(content, prompt_after_intro, engine)


def generate_until_length(min_length, tries):
    pass


def google_search(engine='curie'):
    search_query = input("Search Google: ")
    create_google_search_page(search_query, 8, engine=engine)
    print('done')


# TODO option to specify first line
# TODO infobox option
# TODO set image

def wiki_article(title, infobox=False, img=None, start_text=None, save_as='auto', engine='cushman-alpha'):
    content = {}
    content['title'] = title
    content['url'] = title.replace(" ", "_")
    if infobox or (img is not None):
        content['infobox'] = {}
    if img is not None:
        content['infobox']['img'] = {}
        content['infobox']['img']['filename'] = img['filename']
        content['infobox']['img']['description'] = img['description']
    generate_wiki_article(content, infobox=infobox, start_text=start_text, engine=engine)
    html = wikipedia_html(content)
    if save_as == 'auto':
        filename = f"alternet/wiki/{content['title']}-wikipedia-{engine}.html"
    else:
        filename = f"alternet/wiki/{save_as}.html"
    html_file = open(filename, "w")
    html_file.write(html)
    html_file.close()
    print('done')


def create_article(engine='cushman-alpha'):
    title = input("Browse Wikipedia: ")
    wiki_article(title, engine=engine)


def main():
    #google_search(engine='davinci')
    create_article(engine='cushman-alpha')
    # wiki_article(title='The Random Number God', engine='cushman-alpha')
    # wiki_article(title='The Internet', engine='cushman-alpha')
    # wiki_article(title='Wave-particle duality', img={'filename': 'waveparticle.png',
    #                                 'description': 'computer prediction of \"wave-particle duality\"'},
    #              engine='cushman-alpha')
    # wiki_article(title='Quantum mechanics', img={'filename': 'spookyquantum.png',
    #                                              'description': 'computer prediction of \"spooky quantum mechanics\"'},
    #              engine='cushman-alpha')
    # wiki_article(title='Superintelligence', img={'filename': 'superbird.png',
    #                                              'description': 'computer prediction of \"superintelligence\"'},
    #              engine='cushman-alpha')


if __name__ == "__main__":
    main()