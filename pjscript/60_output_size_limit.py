# Run in Pj or Pjp with either Python. No dataset or extra libraries required.
# Requires the Pj output-size protection preview (not the earlier installed build).
# True deliberately creates more than 4 MiB across two HTML results.
# Expected: one compact "Python output size limit" information panel, no freeze.
# Change to False and run again to verify normal results recover immediately.
EXCEED_LIMIT = True

if EXCEED_LIMIT:
    for index in range(2):
        mzpjShowHtml('<p>' + ('x' * (2300 * 1024)) + '</p>',
                     name='large_result_' + str(index + 1), title='Deliberately oversized output')
else:
    mzpjShowTable([{'Test': 'Recovery after oversized output', 'Status': 'OK'}],
                  name='recovery', title='Normal output restored')
    mzpjShowText('The size protection does not prevent subsequent script execution.')
