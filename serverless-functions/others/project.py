
def indexMapping(es, project):
    """
    Creates mapping for a project's casebase.
    """
    index_name = project['casebase']
    res = { 'acknowledged' : False }
    if not es.indices.exists(index=index_name):
        # print("Casebase does not exist. Creating casebase index mapping...")
        mapping = {}  # create mapping
        mapping['mappings'] = {}
        mapping['mappings']['properties'] = {}
        for attrib in project['attributes']: # use the project's attributes' specification to determine mapping
            mapping['mappings']['properties'].update(
                {attrib['name']: getMappingFrag(attrib['type'], attrib['similarity'])})
        mapping['mappings']['properties'].update(
            {'hash__': {'type': 'keyword'}})  # keeps hash of entry for easy discovery of duplicates
        # print(mapping)
        # print("Creating casebase index...")
        res = es.indices.create(index=index_name, body=mapping)
        # if res['acknowledged']: # update project to indicate that a casebase has been created (ES can add but not update mappings)
        #   print("Index created for casebase, " + project['name'])
    return res


def getProjectMapping():
    """
    Index mapping for projects. Details of all projects are held in the same index with separate indices for their casebases.
    """
    pmap = {
        "mappings": {
            "properties": {
                "name": {"type": "text"},
                "description": {"type": "text"},
                "casebase": {"type": "text"},
                "hasCasebase": {"type": "boolean"},
                "retainDuplicateCases": {"type": "boolean"},
                "attributes": {
                    "type": "nested",
                    "properties": {
                            "name": {"type": "keyword"},
                            "type": {"type": "keyword"},
                            "similarity": {"type": "keyword"}
                    }
                }
            }
        }
    }
    return pmap


def getMappingFrag(attrType, simMetric):
    """
    Generate mapping fragment for indexing a variety of document fields using Elasticsearch Reference v7.6.
    """
    res = {}
    if attrType == "String" and simMetric == "Semantic USE":
        # dimension for universal sentence encoder. May require passing in as parameter if using vectors of a different dimension
        res['properties'] = {"name": {"type": "keyword"},
                             "rep": {"type": "dense_vector", "dims": 512}}
    elif attrType == "String" and not (simMetric == "Equal"):
        res['type'] = "text"
    elif attrType == "Boolean":
        res['type'] = "boolean"
    elif attrType == "Integer":
        res['type'] = "integer"
    elif attrType == "Float":
        res['type'] = "float"
    elif attrType == "DateString":
        res['type'] = "keyword"
    elif attrType == "Date":
        res['type'] = "date"
        res['format'] = "dd-MM-yyyy||dd-MM-yyyy HH:mm:ss||yyyy-MM-dd||yyyy-MM-dd HH:mm:ss||epoch_millis"
    elif attrType == "Autocomplete":
        res['type'] = "search_as_you_type"
    elif attrType == "Location":
        res['type'] = "geo_point"
    else:
        res['type'] = "keyword"
    return res
