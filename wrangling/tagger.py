""""Creates a joint analysis tag - creating a tags field if item doesn't already,
   have one or append ja tag if it does"""


def make_ja_tag_patch(res):
    # import pdb; pdb.set_trace()
    tag = 'Joint Analysis 2018'
    if res.get('tags'):
        tags = res['tags'].append(tag)
    else:
        tags = [tag]
    return {'tags': tags}


def main():
    # items = ['1324d727-2ac8-4622-8ad3-b6e209235087', '1324d727-2ac8-4622-8ad3-b6e209235087', \"blah\", \"e58e2141-9253-4c91-85c3-d67ce06db28f\"]
    # items = [\"431106bc-8535-4448-903e-854af460b260\"]
    types2exclude = ['OntologyTerm', 'Ontology', 'Lab', 'User', 'Award', 'ExperimentSetReplicate']
    releasable = get_types_that_can_have_field('public_release')
    #search = '/search/?status=released&type=Biosource'
    #search = '/search/?type=ExperimentSetReplicate&experimentset_type=replicate&experiments_in_set.experiment_type=repliseq&status=released'
    search = '/search/?date_released%21=No%20value&experimentset_type=replicate&lab.title=Erez%20Lieberman%20Aiden%2C%20BCM&lab.title=Job%20Dekker%2C%20UMMS&lab.title=Bing%20Ren%2C%20UCSD&lab.title=Rene%20Maehr%2C%20UMMS&status=released&type=ExperimentSetReplicate'
    res = fdnDCIC.get_FDN(search, ff)

    bsuuids = []

    for item in res['graph']:
        bsuuids.append(item['uuid'])

    seen = []
    count = 0
    for item in res['graph']:
        uid = item['uuid']
        reldate = item['date_released']
        count = count + 1
        print '\\nWorking on ', uid, count
        linked = {}
        linked = get_linked_items(uid, linked)
        flinked = filter_dict_by_value(linked, types2exclude, include=False)
        for i, t in flinked.iteritems():
            if i not in seen:
                print i, t
                seen.append(i)
                # import pdb; pdb.set_trace()
                item = fdnDCIC.get_FDN(i, ff)
                if 'public_release' not in item or 'date_released' not in item:
                    if t in releasable:
                        patch = {'public_release': reldate}
                        dry_run = False
                        if not dry_run:
                            pres = fdnDCIC.patch_FDN(i, ff, patch)
                            print pres
                            print "--SUCCESS!"
                        print "Adding Public Release Date %s to %s of type %s" % (reldate, i, t)
    #taggable = get_types_that_can_have_field('tags')

    #for it in items:
    #    linked = get_linked_items(it, linked)

    # more efficient to do this on the full dict rather than item by item
    #items2tag = filter_dict_by_value(linked, taggable)
    #for it, ty in items2tag.iteritems():
        # import pdb; pdb.set_trace()
        #res = fdnDCIC.get_FDN(it, ff)
        #if not has_field_value(res, 'tags', 'Joint Analysis'):
            # patch the item with the tag
            #patch = make_ja_tag_patch(res)
            #dry_run = True
            #if not dry_run:
                #patch = fdnDCIC.patch_FDN(it, ff, patch)
                #print patch
                #print \"--SUCCESS!\"
            #print \"Adding JA tag to %s of type %s\" % (it, ty)

    #linked = filter_dict_by_value(linked, exclude, include=False)

    #for l, t in linked.iteritems():
    #    print 'GOT IT: ', l, '\\t', t


if __name__ == '__main__':
    main()
