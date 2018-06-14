 #!/bin/bash
 
echo "Extracting archive"
unzip -o export.zip
echo "Beginning import"
python ./import.py apple_health_export/export.xml