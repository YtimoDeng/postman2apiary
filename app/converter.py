"""
    Tool for generating Blueprint API markup or the Apiary API
    from a Postman collection
    Author: Paul Kinuthia
"""

import json
from urllib.parse import urlparse


class PostmanToApiary:
    def __init__(self, data={}):
        self.file = data.get('postman_collection')
        self.data = {}
        self.name = ''
        self.description = ''
        self.domain = ''
        self.api_version = '/api/v1'
        self.output_file = data.get('output_file')
        self.file_format = 'FORMAT: 1A'
        self.folderNum = 1
        self.resources = {}
        self.folders = []
        self.collection_variable = {}
        self.load_collection_json_data()
        self.get_collection_variable()
        self.get_document_info()
        self.get_folders()

    def load_collection_json_data(self):
        try:
            with open(self.file, encoding='utf-8') as f:
                self.data = json.loads(f.read())
        except Exception as e:
            print('[x] :( Some error occurred')
            print(e)
            exit(0)

    def get_collection_variable(self):
        variables = self.data.get('variable', [])
        for variable in variables:
            self.collection_variable[variable.get('key')] = variable.get('value')

    def get_document_info(self):
        self.name = self.data.get('info', {}).get('name')
        self.description = self.data.get('description', '')
        self.domain = self.collection_variable.get('domain', 'http://localhost')

    def get_folders(self):
        self.folders = self.data.get('item')

    def write(self):
        # write document introduction
        doc = open(self.output_file, 'w+')
        doc.write(self.file_format + '\n')
        doc.write('HOST: ' + self.domain + '\n\n')
        doc.write('# ' + self.name + '\n\n')
        if self.description:
            doc.write(self.description)
        doc.close()

        for folder in self.folders:
            self.process_folder(folder)

    def process_folder(self, folder):
        folderName = folder.get('name', '')
        items = folder.get('item', [])

        for item in items:
            self.process_item(item)

        doc = open(self.output_file, 'a')
        doc.write('# Group ' + str(self.folderNum) + '.' + folderName + '\n\n')
        self.folderNum += 1
        content_type = 'application/json'
        for resourceKey in self.resources:
            resource = self.resources[resourceKey]
            resourceName = '## ' + resource['name'] + ' [/' + resource['path'] + ']\n'
            doc.write(resourceName + '\n\n')
            for method in resource['methods']:
                apiTitle = '### ' + method['method'] + ' '+ resource['path'] + ' [' + method['method'] + ']'
                doc.write(apiTitle + '\n\n')
                if (method['description']): 
                    doc.write(method['description'] + '\n\n')
                try:
                    if method['method'] == "POST" or method['method'] == "PUT":
                        doc.write('+ Request (' + content_type + ')\n\n')
                        doc.write('    + Body\n\n')
                        doc.write('            {')
                        doc.write(json.dumps(method['requestBody'], indent = 14)[1:-1])
                        doc.write('            }\n')
                        doc.write('\n\n\n')
                except Exception as e:
                    pass
                doc.write('+ Response 200 (' + content_type + ')\n\n\n')

        doc.close()

    def process_item(self, item):
        request, response = item.get('request'), item.get('response')
        name, description = item.get('name', ''), item.get('description', '')
        url = request.get('url')
        
        if isinstance(url, object):
            path = '/'.join(url.get('path', []))
        else:
            raise ValueError('Can not find path.')
        
        method = request.get('method', '')
        if method == "POST" or method == "PUT":
            json_data = json.loads(request.get('body').get('raw'))
        else:
            json_data = ''

        methodAttr = {
            'method': method,
            'description': description,
            'requestBody': json_data,
            'responseBody': '',
        }

        if path in self.resources:
            self.resources[path]['methods'].append(methodAttr)
        else:
            self.resources[path] = {
                "path" : path,
                "name" : name,
                "methods" : [
                    methodAttr
                ],
            };
        
        


if __name__ == "__main__":
    data = dict()
    data['postman_collection'] = '/home/wishmobile/Tools/testPostman2Apiary.json'
    data['output_file'] = '/home/wishmobile/Tools/test.apib'
    app = PostmanToApiary(data)
    app.write()
    # app.main()

