import csv
import datetime, time

import general_lib


###
#   Create comparison matrix
#   input_file: The file that contains the data. Built up with rows as entries; columns are the
#               variables. One column contains the ID of the entry.
#   output_file:The file whereto the comparison matrix will be written.
#   id_label:     One of the columns must be a unique ID for the entries. This specifies the label.
#   headers:    All columns are labeled with headers. If the file does not contain the headers,
#               specify them in the variable headers.
###
def CreateComparisonMatrix(input_file, output_file, id_label, headers = ''):
    # dbg_file = open('debug_output','wt')
    print('Processing comparison:')
    print(' - input file: {0}'.format(input_file))
    print(' - output file: {0}'.format(output_file))
    start_time = datetime.datetime.now()

    # Open input file two times
    csvfile = 0
    csvfile2 = 0
    try:
        csvfile = open(input_file, 'rt')
        csvfile2 = open(input_file, 'rt')
    except IOError:
        print('Error: Could not find input file {0}.'.format(input_file))
        exit()

    # Try to see if file has a header.
    data_reader = csv.reader(csvfile, delimiter=';', quotechar='\'')
    file_has_headers = csv.Sniffer().has_header(csvfile.read(1024))

    # Read the headers
    if file_has_headers:
        if headers != '':
            print('Error: Headers are defined twice. Exciting!')
            exit()
        csvfile.seek(0)
        headers = next(data_reader)
        # print(headers)

    # Check if the headers were properly specified.
    if headers == '':
        print('Error: No headers were specified. Exciting!')
        exit()
    else:
        for label in headers:
            if headers.count(label)!=1:
                print('Error: The headers contain at least one duplicate entry({0}). Exciting!'.format(label))
                exit()

    # Check if the id_label was properly specified.
    if id_label == '':
        print('Error: No id_label was specified. Exciting!'.format(id_label))
        exit()
    elif headers.count(id_label)<1:
        print('Error: The id_label({0}) was not found in the header list. Exciting!\n({1})'.format(id_label, headers))
        exit()
    elif headers.count(id_label)>1:
        print('Error: The id_label({0}) was found more than once in the header list. Exciting!\n({1})'.format(id_label, headers))
        exit()

    # Open output file for writing text.
    if not general_lib.ensure_dir(output_file, True):
        print('Error: Could not create output directory for file {0}.'.format(output_file))

    # comparisonMatrix = open(output_file, 'wt')
    comparisonMatrix = 0
    try:
        comparisonMatrix = open(output_file, 'wt')
    except IOError:
        print('Error: Could not open output file {0}.'.format(output_file))
        exit()

    # Open two DictReader objects, one on each file.
    reader = csv.DictReader(csvfile, delimiter=';', fieldnames=headers)
    reader2 = csv.DictReader(csvfile2, delimiter=';', fieldnames=headers)

    # Read all IDs with the id_label and write them to the output file as new headers.
    csvfile.seek(0)
    # outBuff = '{0};'.format(id_label)
    outBuff = ';'.join(str(row[id_label]) for row in reader)
    outBuff += '\n'
    comparisonMatrix.write(outBuff)

    outBuff = ''
    rows = 0
    columns = 0
    csvfile.seek(0)
    if file_has_headers:
        next(reader)
    for dict_row in reader:
        # print(dict_row)
        rows += 1
        if id_label in dict_row:
            outBuff += '{0}'.format(dict_row[id_label])
        else:
            print('Error: No label found in the header with the id_label({0}). Exciting!'
                  .format(id_label))
            exit()
        # reader_line_num = reader.line_num
        # csvfile2.seek(reader_line_num)
        csvfile2.seek(0)
        if file_has_headers:
            next(reader2)
            # print('Skipped first row, because it seems to be a header.')
        columns = 0
        for dict_row2 in reader2:
            columns += 1
            dbg_comp_str = ""
            num_equal = 0
            num_vars = len(headers)
            if id_label != "":
                num_vars -= 1
            # print('number of variables: {0}'.format(num_vars))
            for hdr_key in headers:
                if hdr_key == id_label:
                    continue
                dbg_comp_str = " - {0},{1}: ".format(dict_row2[id_label], hdr_key)
                val_1 = dict_row[hdr_key]
                val_2 = dict_row2[hdr_key]
                dbg_comp_str = "{0}{1}?={2}".format(dbg_comp_str, val_1, val_2)
                if val_1 == val_2:
                    num_equal += 1
                    dbg_comp_str = "{0} => {1}".format(dbg_comp_str, num_equal)
                # dbg_file.write(dbg_comp_str)
            perc_match = num_equal/num_vars
            # dbg_file.write('{0}/{1}={2}'.format(num_equal, num_vars, perc_match))
            outBuff += ";{0:.2f}".format(float(perc_match))
        outBuff += "\n"
        comparisonMatrix.write(outBuff)
    comparisonMatrix.close()
    csvfile.close()
    csvfile2.close()
    end_time = datetime.datetime.now()
    duration = end_time-start_time
    print(' - Created a matrix {0} by {1}.'.format(rows,columns))
    print(' - Took: {0:.0f}h{1:.0f}m{2:.0f}s {3:.0f}ms'.format(float(duration.seconds/3600),
                                               float(duration.seconds/60 % 60),
                                               float(duration.seconds % 60),
                                               float(duration.microseconds/1000)))
    print()
# end CreateComparisonMatrix


###
#   Average the matrices from the provided files in the list and export it.
#   filePathList:   List containing the matrices. The matrices should have column and row headers.
#                   It is assumed that the row(vert) and column(hori) headers are the first.
#   output_file:    The file to where the resulting matrix will be written.
###
def AverageMatrices(filePathList, output_file, id_label):
    num_files = len(filePathList)
    if num_files == 1:
        print('Only one? That means your done.')
        return
    elif num_files < 1:
        print('No matrices specified. Exciting!')
        exit()
    print('Merging matrices({}):'.format(num_files))
    start_time = datetime.datetime.now()
    headers = []
    fileList = []
    readerList = []
    has_headers = False

    # Open all files
    print(' - input files:')
    for filePath in filePathList:
        print(' - file: {0}'.format(filePath))
        file = open(filePath, 'rt')
        if file.readable():
            fileList.append(file)
            # file_dialect = csv.Sniffer().sniff(file.read(128),delimiters=[';'])
            # print('file_dialect{0}'.format(file_dialect))
            has_headers = csv.Sniffer().has_header(file.read(128))
            if not has_headers:
                print('Error: File has no headers. Exciting!')
                exit()
        else:
            print('Error: File is not readable. Exciting!')
            exit()

    print(' - output file: {0}'.format(output_file))
    outWriter = open(output_file,'wt')
    # TODO: check if open

    # Create a reader for each file in fileList and Get headers
    the_headers = ['empty header list']
    for file in fileList:
        file.seek(0)
        data_reader = csv.reader(file, delimiter=';')
        headers = next(data_reader)
        if len(the_headers) > 0 and the_headers[0] == 'empty header list':
            the_headers = headers
        if sorted(the_headers) != sorted(headers):
            print('Error: The headers of the files are not the same. Exciting!')
            print(' - the_headers: {0}'.format(the_headers))
            print(' - new headers: {0}'.format(headers))
            exit()

        # Create the reader
        reader = csv.DictReader(file, delimiter=';', fieldnames=headers)
        readerList.append(reader)
    print(headers)

    # Check if the id_label was properly specified.
    if id_label == '':
        print('Error: No id_label was specified. Exciting!'.format(id_label))
        exit()
    elif headers.count(id_label)<1:
        print('Error: The id_label({0}) was not found in the header list. Exciting!\n({1})'.format(id_label, headers))
        exit()
    elif headers.count(id_label)>1:
        print('Error: The id_label({0}) was found more than once in the header list. Exciting!\n({1})'.format(id_label, headers))
        exit()

    # Write headers to output file.
    outBuff = ';'.join(str(lbl) for lbl in headers)
    outBuff += '\n'
    outWriter.write(outBuff)

    # for each row of the first matrix.
    first_reader = readerList[0]
    for row_of_first in first_reader:
        rows = []
        outValues = []

        # open the same row of the rest of the matrices.
        rows.append(row_of_first)
        for reader in readerList[1:]:
            row = next(reader)
            rows.append(row)

        # TODO: check id_label to be the same.

        # Write id_label to output buffer.
        outBuff = '{0}'.format(str(row_of_first[id_label]))

        # for all labels (variables) in the headers list do
        for label in headers:
            if label == headers[0]:
                continue
            if label == '':
                print('Error: Header contains an empty label. Exciting!')
                exit()
            rowSum = 0
            numRows = 0
            sum_print = '{0} @ {1}:\t'.format(row_of_first[id_label], label)
            for row in rows:
                value = row[label]
                if value == '':
                    print('Error: matrix contains an empty value. Exciting!')
                    exit()
                rowSum += float(value)
                numRows += 1
                sum_print += '+{0:.2f}={1:.2f} '.format(float(value), rowSum)
            value_out = 999;
            if not numRows == 0:
                value_out = rowSum/numRows
            else:
                print('Error: Division by zero. Exciting!')
            sum_print += '  {0:.2f}/{1:.2f}={2:.2f}'.format(rowSum, numRows, value_out)
            outValues.append(value_out)
            print(sum_print)
        for val in outValues:
            outBuff += ';{0:.2f}'.format(float(val))
        outBuff += '\n'
        outWriter.write(outBuff)
        print()

    end_time = datetime.datetime.now()
    duration = end_time-start_time
    # print(' - Created a matrix {0} by {1}.'.format(rows,columns))
    print(' - Took: {0:.0f}h{1:.0f}m{2:.0f}s {3:.0f}ms'.format(float(duration.seconds/3600),
                                               float(duration.seconds/60 % 60),
                                               float(duration.seconds % 60),
                                               float(duration.microseconds/1000)))
    print()
# end AverageMatrices
