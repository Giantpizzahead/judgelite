#!/bin/sh

# Delete the below 2 lines once you've added the remote server location to the rsync command below.
echo "Please edit the upload script to add the location of the JudgeLite server before running this script."
exit 1

echo "Converting CRLF to LF for all test cases..."
rm -rf temp_upload_output
mkdir temp_upload_output

cp -r problem_info temp_upload_output/problem_info

cd temp_upload_output || exit

find . \( -name "*.in" -o -name "*.out" \) | while read txt; do
	dos2unix $txt
done

echo "Uploading to JudgeLite..."
# rsync -Pav -e "ssh -i <SSH_KEY_HERE>" problem_info/ <USERNAME@REMOTE_HOST_IP>:judgelite/problem_info
echo "Upload complete!"
