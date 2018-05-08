import LoesiesLib

input_file = './data/Janneke/BoutJanneke1_ISO8859-15.csv'
# input_file = './data/Janneke/BoutJanneke1_UTF-8.csv'
# input_file = './data/Janneke/BoutJanneke1.csv'
# output_file = './data/Janneke/BoutJannekeOut.csv'
output_file = ''
# id_label = 'Dognr'
LoesiesLib.FindBouts(input_file, output_file, 'act', 1)
