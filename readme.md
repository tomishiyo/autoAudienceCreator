# Auto Audience Creator
In SFMC, creating multiple DEs, automations and folders can be a time intensive process when done through the UI.

This Python script seeks to automate this process by making REST and SOAP API calls.

The following objects are created under the BU of the installed package when the script is executed:
1) A shared folder named as the campaign name
2) Two shared data extensions for each language. These are identical except for the fact that one of them is sendable (Subscriber Key relates to Subscriber Key on All Subscribers). Data retention is configured to 6 months, deleting all records and the data extension.
3) One additional shared data extension used for QA.

## Use instructions
1) Rename EXAMPLE_credentials.txt and EXAMPLE_inputs.txt to credentials.txt and inputs.txt
2) In your SFMC, create an installed package with the necessary permissions (TBW), and take note of the client id, client secret and API domain.
3) Insert this information in the corresponding lines on credentials.txt
4) Edit inputs.txt and choose the parent folder ID (you can find a folder's ID via the UI in SFMC), the campaign name and number of languages.
5) Edit the EXAMPLE_payload.xml file. Make two copies, naming one as de_payload.xml and the other as qa_de_payload.xml. In these files, add or remove data extension fields as required, following the model shown. Consult https://developer.salesforce.com/docs/marketing/marketing-cloud/guide/dataextensionfield.html for additional details on the fields.
6) Install requirements with
```pip install -r requirements.txt```
7) Run the script with ```python autoAudience.py```

For best results, it is recommended to run the script in a separated virtual environment.

## Known issues
The data extensions are not created with the correct retention settings (delete all records after 6 months). They were created as modelled by the documentation, so this needs further investigation.

## To do
- Implement creation of automation and query folders.
- Implement creation of the automation.
- Implement creation of the query activities.
