import csv, sys
import datetime, time

from .general_lib import *


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
    # general_lib.
    if not ensure_dir(output_file, True):
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
            outBuff = '{0}'.format(dict_row[id_label])
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
    sys.stdout.flush()
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
    sys.stdout.flush()
# end AverageMatrices


from enum import Enum
import os

###
#   Create comparison matrix
#   input_file: The file that contains the data. Built up with rows as entries; columns are the
#               variables. One column contains the ID of the entry.
#   output_file:The file whereto the comparison matrix will be written.
#   id_label:     One of the columns must be a unique ID for the entries. This specifies the label.
#   headers:    All columns are labeled with headers. If the file does not contain the headers,
#               specify them in the variable headers.
###
def FindBouts(input_file, output_file='', labels={'act_label':'act','id_label':''}, score_level=1, options = {'skip_missing_values':True}):
    # Settings
    headers = ''
    distinguishing_ids = False
    entryTime = 15
    class ActBout(Enum):
        REST = 0
        WAKE = 1

    if output_file=='':
        fileSet = os.path.splitext(input_file)
        output_file = '{0}_out{1}'.format(fileSet[0],fileSet[1])
    # dbg_file = open('debug_output','wt')
    print('Processing score files for bouts:')
    print('\t- input file:\t{0}'.format(input_file))
    print('\t- output file:\t{0}'.format(output_file))

    # Name the labels chosen.
    print('')
    if not 'act_label' in labels:
        labels['act_label']='act'
    print('Using labels:')
    if 'act_label' in labels:
        print(' - \t[{0}] as activity label'.format(labels['act_label']))
    if 'id_label' in labels:
        print(' - \t[{0}] as Id label'.format(labels['id_label']))
        distinguishing_ids = True
    if 'time_label' in labels:
        print(' - \t[{0}] as time label'.format(labels['time_label']))

    # Name the options chosen.
    print('')
    print('Options:')
    for key,value in options.items():
        print(' - \t{0}:\t{1}'.format(key,value))
    options['skip_missing_values']
    start_time = datetime.datetime.now()

    # Open input file two times
    csvInFile = 0
    try:
        csvInFile = open(input_file, 'rt', encoding='windows-1252')
    except IOError:
        print('Error: Could not find input file {0}.'.format(input_file))
        exit()

    # Try to see if file has a header.
    print('')
    data_reader = csv.reader(csvInFile, delimiter=';', quotechar='\'')
    file_has_headers = csv.Sniffer().has_header(csvInFile.read(1024))

    # Read the headers
    if file_has_headers:
        # if headers != '':
            # print('Error: Headers were already defined. So now they are defined twice. Exciting!')
            # exit()
        csvInFile.seek(0)
        headers = next(data_reader)
        print('Using headers:\n\t{0}'.format(headers))
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

    # Check if the act_label was properly specified.
    if labels['act_label'] == '':
        print('Error: No act_label was specified. Exciting!'.format(labels['act_label']))
        exit()
    elif headers.count(labels['act_label'])<1:
        print('Error: The act_label({0}) was not found in the header list. Exciting!\n({1})'.format(labels['act_label'], headers))
        exit()
    elif headers.count(labels['act_label'])>1:
        print('Error: The act_label({0}) was found more than once in the header list. Exciting!\n({1})'.format(labels['act_label'], headers))
        exit()

    # Open input file as dictReader.
    dict_reader = csv.DictReader(csvInFile, delimiter=';', fieldnames=headers)

    # Open output file for writing text.
    # general_lib.
    if not ensure_dir(output_file, True):
        print('Error: Could not create output directory for file {0}.'.format(output_file))

    csvOutFile = 0
    try:
        csvOutFile = open(output_file, 'wt')
    except IOError:
        print('Error: Could not open output file {0}.'.format(output_file))
        exit()

    cont = input("\nPress Enter to continue. (or ctrl-c to exit)\n")


    id_val = -1
    if distinguishing_ids:
        for current_row, next_row in pairwise(dict_reader):
            id_val = current_row[labels['id_label']]
        print('ID: {0}'.format(id_val))



    # Print output headers to file
    outBoutList = []
    outBoutList.append('BType')
    outBoutList.append('time')
    outBoutList.append('raw')
    outBuff = ';'.join(outBoutList)
    outBuff = outBuff +'\n'
    csvOutFile.write(outBuff)

    # Initialse
    outBoutList = []
    BoutsCountList = [0,0]
    BoutsTotalTImeList = [0,0]
    BoutsMeanTImeList = [0,0]

    rawActList = []
    timeBout = 0
    firstAct = True
    number_of_entries = 0
    skipped_missing_values = 0
    # newAct = 0
    # currAct = 0
    outBuff = ''

    for in_row in dict_reader:
        number_of_entries = number_of_entries + 1
        # print('OUT: {0}'.format(in_row[labels['act_label']]))
        act_val=-1
        time_val = -1

        try:
            act_val = int(in_row[labels['act_label']])
        except ValueError:
            act_val = 0
            if options['skip_missing_values']:
                skipped_missing_values = skipped_missing_values + 1
                # print('The activity value read for {1} is [{0}], skipping value.'.format(act_val,in_row.items()))
                continue
            else:
                print('The activity value read for {2} is [{0}], using {1}.'.format(in_row[labels['act_label']],act_val,in_row.items()))

        if 'time_label' in labels:
            try:
                time_val = int(in_row[labels['time_label']])
            except ValueError:
                time_val = 0
                    # print('The activity value read for {1} is [{0}], skipping value.'.format(act_val,in_row.items()))
                print('The row has an invalid time entry: [{0}].'.format(in_row[labels['time_label']]))

        if distinguishing_ids:
            id_val = in_row[labels['id_label']]
            print('The row has an invalid time entry: [{0}].'.format(in_row[labels['time_label']]))


        if act_val<score_level:
            newAct = 0
            # print('low')
        else:
            newAct = 1
            # print('high')

        if (firstAct):
            currAct = newAct
            outBuff = '{0} : '.format('wake' if currAct>=score_level else 'rest')
            outBoutList.append('{0}'.format('wake' if currAct>=score_level else 'rest'))
            firstAct = False

        if currAct != newAct:
            # print('-bout-\n')
            # New bout found
            outBoutList.append('{0}'.format(timeBout))
            rawBuff = '['+ ','.join(rawActList)+']'
            outBoutList.append(rawBuff)
            outBuff = ';'.join(outBoutList)
            outBuff = outBuff +'\n'
            csvOutFile.write(outBuff)

            BoutsCountList[currAct] = BoutsCountList[currAct] + 1
            BoutsTotalTImeList[currAct] = BoutsTotalTImeList[currAct] + timeBout
            BoutsMeanTImeList[currAct] = BoutsTotalTImeList[currAct] / BoutsCountList[currAct]

            timeBout = 0
            outBoutList = []
            rawActList = []
            currAct = newAct
            outBoutList.append('{0}'.format('wake' if currAct>=score_level else 'rest'))

        rawActList.append('{0}'.format(str(in_row[labels['act_label']])))
        if 'time_label' in labels:
            timeBout = timeBout + timeAct
        else:
            timeBout = timeBout + entryTime

    # Last bout found
    outBoutList.append('{0}'.format(timeBout))
    rawBuff = '['+ ','.join(rawActList)+']'
    outBoutList.append(rawBuff)
    outBuff = ';'.join(outBoutList)
    outBuff = outBuff +'\n'
    csvOutFile.write(outBuff)

    BoutsCountList[currAct] = BoutsCountList[currAct] + 1
    BoutsTotalTImeList[currAct] = BoutsTotalTImeList[currAct] + timeBout
    BoutsMeanTImeList[currAct] = BoutsTotalTImeList[currAct] / BoutsCountList[currAct]

    timeBout = 0

    outBuff = '\n'
    outBuff = outBuff + 'Number of bouts:\n'
    outBuff = outBuff + '\t- rest :\t{0: 8}\n'.format(BoutsCountList[ActBout.REST.value])
    outBuff = outBuff + '\t- wake :\t{0: 8}\n'.format(BoutsCountList[ActBout.WAKE.value])
    outBuff = outBuff +'\n'
    outBuff = outBuff + 'Total time per bout type:\n'
    outBuff = outBuff + '\t- rest :\t{0: 8}\n'.format(BoutsTotalTImeList[ActBout.REST.value])
    outBuff = outBuff + '\t- wake :\t{0: 8}\n'.format(BoutsTotalTImeList[ActBout.WAKE.value])
    outBuff = outBuff +'\n'
    outBuff = outBuff + 'Mean time per bout type:\n'
    outBuff = outBuff + '\t- rest :\t{0: 6.9}\n'.format(BoutsMeanTImeList[ActBout.REST.value])
    outBuff = outBuff + '\t- wake :\t{0: 6.9}\n'.format(BoutsMeanTImeList[ActBout.WAKE.value])
    outBuff = outBuff +'\n'
    outBuff = outBuff +'\n'
    outBuff = outBuff + 'Number entries:\t\t\t{0: 8}\n'.format(number_of_entries)
    outBuff = outBuff + 'Number of skipped entries:\t{0: 8}\n'.format(skipped_missing_values)

    csvOutFile.write(outBuff)

    print(outBuff)

    sys.stdout.flush()

# end FindBouts
