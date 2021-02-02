t_0 = 15
t_1 = 16
t_2 = 17
t_3 = 18
t_4 = 19
t_5 = 20
t_6 = 21
t_7 = 22
t_8 = 23
t_9 = 24
t_10 = 940
t_11 = 1157
t_12 = 1065
t_13 = 1485

anti_num_mask = {t_0: -100,
                 t_1: -100,
                 t_2: -100,
                 t_3: -100,
                 t_4: -100,
                 t_5: -100,
                 t_6: -100,
                 t_7: -100,
                 t_8: -100,
                 t_9: -100,
                 t_10: -100}

t_23 = 1954

t_point = 13

t_NEWLINE = 198
t_is = 271
t_was = 9776
t_are = 533
t_oparen = 7
t_From = 4863

t_Browse = 32635

t_References = 19927

# used at beginning of sections to prevent first token from being a number or newline
section_begin_mask = {**anti_num_mask, **{t_NEWLINE: -100}}

TOC_first_token_mask = {t_2: -100,
                        t_23: -100,
                        t_NEWLINE: -100,
                        t_Browse: -100,
                        t_point: -100}

TOC_first_line_mask = {t_2: -100}

TOC_secondline_mask = {t_point: 95, t_2: 90}

# TODO discourages infinite siblings but encourages infinite nesting
# TODO forbid more than 3 levels of nesting?
TOC_rest_mask = {t_6: -1,
                 t_7: -3,
                 t_8: -8,
                 t_9: -15,
                 t_10: -30,
                 t_11: -50,
                 t_12: -80,
                 t_13: -100,
                 t_0: -100,
                 t_References: 2}

# JAN, FEB, etc
DATE_MASK = {12128: 100,
             15146: 100,
             7676: 100,
             13680: 100,
             6747: 100,
             22396: 100,
             16980: 100,
             12512: 100,
             19117: 100,
             20795: 100,
             10707: 100}

lowercase_mask = {64: 100,
                  65: 100,
                  66: 100,
                  67: 100,
                  68: 100,
                  69: 100,
                  70: 100,
                  71: 100,
                  72: 100,
                  73: 100,
                  74: 100,
                  75: 100,
                  76: 100,
                  77: 100,
                  78: 100,
                  79: 100,
                  80: 100,
                  81: 100,
                  82: 100,
                  83: 100,
                  84: 100,
                  85: 100,
                  86: 100,
                  87: 100,
                  88: 100,
                  89: 100}

uppercase_mask = {32: 100,
                  33: 100,
                  34: 100,
                  35: 100,
                  36: 100,
                  37: 100,
                  38: 100,
                  39: 100,
                  40: 100,
                  41: 100,
                  42: 100,
                  43: 100,
                  44: 100,
                  45: 100,
                  46: 100,
                  47: 100,
                  48: 100,
                  49: 100,
                  50: 100,
                  51: 100,
                  52: 100,
                  53: 100,
                  54: 100,
                  55: 100}

digit_mask = anti_num_mask = {t_0: 100,
                              t_1: 100,
                              t_2: 100,
                              t_3: 100,
                              t_4: 100,
                              t_5: 100,
                              t_6: 100,
                              t_7: 100,
                              t_8: 100,
                              t_9: 100}

punctuation_mask = {13: 100,
                    11: 100,
                    30: 100,
                    26: 100,
                    25: 100,
                    14: 100,
                    7: 100,
                    8: 100,
                    1: 100,
                    6: 100,
                    0: 100,
                    12: 100,
                    10: 100,
                    28: 100,
                    27: 100,
                    29: 100,
                    5: 100,
                    4: 100,
                    62: 100}

punctuation_space_mask = {764: 100,
                          837: 100,
                          5633: 100,
                          2162: 100,
                          1058: 100,
                          1220: 100,
                          357: 100,
                          1267: 100,
                          366: 100,
                          705: 100,
                          5145: 100,
                          532: 100,
                          1343: 100,
                          796: 100,
                          1279: 100,
                          1875: 100,
                          1222: 100,
                          4064: 100,
                          4808: 100}

lowercase_space_mask = {257: 100,
                        275: 100,
                        269: 100,
                        288: 100,
                        304: 100,
                        277: 100,
                        308: 100,
                        289: 100,
                        1312: 100,
                        474: 100,
                        479: 100,
                        300: 100,
                        285: 100,
                        299: 100,
                        267: 100,
                        279: 100,
                        10662: 100,
                        374: 100,
                        264: 100,
                        256: 100,
                        334: 100,
                        410: 100,
                        266: 100,
                        2124: 100,
                        331: 100,
                        1976: 100}

uppercase_space_mask = {317: 100,
                        347: 100,
                        327: 100,
                        360: 100,
                        412: 100,
                        376: 100,
                        402: 100,
                        367: 100,
                        314: 100,
                        449: 100,
                        509: 100,
                        406: 100,
                        337: 100,
                        399: 100,
                        440: 100,
                        350: 100,
                        1195: 100,
                        371: 100,
                        311: 100,
                        309: 100,
                        471: 100,
                        569: 100,
                        370: 100,
                        1395: 100}

digits_space_mask = {657: 100,
                     352: 100,
                     362: 100,
                     513: 100,
                     604: 100,
                     642: 100,
                     718: 100,
                     767: 100,
                     807: 100,
                     860: 100}

single_char_mask = {**lowercase_mask, **uppercase_mask, **digit_mask, **punctuation_mask, **{t_NEWLINE: 100}}

single_char_space_mask = {**single_char_mask, **digits_space_mask, **punctuation_space_mask, **lowercase_space_mask,
                          **uppercase_space_mask}
