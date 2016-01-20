import LoesiesLib

print('Dog Data.')

input_file = './data/data.csv'
output_file = './data/output/data_matrix.csv'
id_label = 'Dognr'
LoesiesLib.CreateComparisonMatrix(input_file, output_file, id_label)


print('Randomised Data.')

filePathList = []

input_file_body = './data/random/body77_sampled.csv'
output_file_body = './data/random/output/body77_sampled_matrix.csv'
id_label = 'Dognr'
LoesiesLib.CreateComparisonMatrix(input_file_body, output_file_body, id_label)
filePathList.append(output_file_body)

input_file_head = './data/random/head77_sampled.csv'
output_file_head = './data/random/output/head77_sampled_matrix.csv'
id_label = 'Dognr'
LoesiesLib.CreateComparisonMatrix(input_file_head, output_file_head, id_label)
filePathList.append(output_file_head)

input_file_heart = './data/random/heart77_sampled.csv'
output_file_heart = './data/random/output/heart77_sampled_matrix.csv'
id_label = 'Dognr'
LoesiesLib.CreateComparisonMatrix(input_file_heart, output_file_heart, id_label)
filePathList.append(output_file_heart)

input_file_lip = './data/random/lip77_sampled.csv'
output_file_lip = './data/random/output/lip77_sampled_matrix.csv'
id_label = 'Dognr'
LoesiesLib.CreateComparisonMatrix(input_file_lip, output_file_lip, id_label)
filePathList.append(output_file_lip)

input_file_pant = './data/random/pant77_sampled.csv'
output_file_pant = './data/random/output/pant77_sampled_matrix.csv'
id_label = 'Dognr'
LoesiesLib.CreateComparisonMatrix(input_file_pant, output_file_pant, id_label)
filePathList.append(output_file_pant)

# Create list of all the output files of the comparison to enter into the AverageMatrices function.
output_file = './data/random/output/all_sampled_matrix.csv'
LoesiesLib.AverageMatrices(filePathList, output_file, 'Dognr')




