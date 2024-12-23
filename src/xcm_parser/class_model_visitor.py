""" class_model_visitor.py """

from arpeggio import PTNodeVisitor
from collections import namedtuple

ID_a = namedtuple('ID_a', 'number superid')
"""Class identifier"""
Subsystem_a = namedtuple('Subsystem_a', 'subsystem domain classes rels metadata')
"""Complete subsystem class model along with subsystem and metadata header and domain data"""

class SubsystemVisitor(PTNodeVisitor):

    # Root
    @classmethod
    def visit_subsystem(cls, node, children):
        """
        (LINEWWRAP* EOF) / (metadata? domain_header subsystem_header class_set rel_section? EOF)
        """
        metadata = children.results.get('metadata', None)
        subsys_name = children.results['subsystem_header'][0]  # Required by model parser
        domain_name = children.results['domain_header'][0]  # Required by model parser
        class_data = children.results['class_set'][0]  # Required by model parser
        rel_data = children.results.get('rel_section', [])  # Optional section
        return Subsystem_a(
            subsystem=subsys_name, domain=domain_name,
            classes=class_data, rels=rel_data if not rel_data else rel_data[0],
            metadata=None if not metadata else metadata[0]
        )

    # Metadata
    @classmethod
    def visit_metadata(cls, node, children):
        """ metadata_header data_item* """
        items = {k: v for c in children for k, v in c.items()}
        return items

    @classmethod
    def visit_text_item(cls, node, children):
        """ ':' SP* r'.*' """
        return children[0], False  # Item, Not a resource

    @classmethod
    def visit_resource_item(cls, node, children):
        """ '>' SP* word (delim word)* """
        return ''.join(children), True  # Item, Is a resource

    @classmethod
    def visit_item_name(cls, node, children):
        """ iword delim word* """
        return ''.join(children)

    @classmethod
    def visit_data_item(cls, node, children):
        """ INDENT item_name SP* (resource_item / text_item) EOL """
        return { children[0]: children[1] }

    # Domain
    @classmethod
    def visit_domain_header(cls, node, children):
        """ "domain" SP domain_name domain_alias EOL """
        items = {k: v for d in children for k, v in d.items()}
        return items

    @classmethod
    def visit_domain_name(cls, node, children):
        """ icaps_name """
        name = ''.join(children)
        return {'name': name }

    @classmethod
    def visit_domain_alias(cls, node, children):
        """ ',' SP acword """
        return { 'alias': children[0] }

    # Subsystem
    @classmethod
    def visit_subsystem_header(cls, node, children):
        """ "subsystem" SP subsystem_name subsystem_alias SP num_range EOL """
        items = {k: v for d in children for k, v in d.items()}
        return items

    @classmethod
    def visit_subsystem_name(cls, node, children):
        """ icaps_name """
        name = ''.join(children)
        return {'name': name }

    @classmethod
    def visit_subsystem_alias(cls, node, children):
        """ ',' SP acword """
        return { 'alias': children[0] }

    @classmethod
    def visit_num_range(cls, node, children):
        """ ordinal '-' ordinal """
        return { 'range': (int(children[0]), int(children[1])) }

    # Classes
    @classmethod
    def visit_class_set(cls, node, children):
        """ class_block* """
        return children

    @classmethod
    def visit_class_block(cls, node, children):
        """
        class_header ee_header? attr_block block_end
        """
        ch = children.results['class_header'][0]
        ablock = children.results['attr_block'][0]
        eeheader = children.results.get('ee_header')
        eeheader = {} if not eeheader else { 'ee' : eeheader[0] }
        return ch | ablock | eeheader

    @classmethod
    def visit_class_name(cls, node, children):
        """ icaps_name """
        name = ''.join(children)
        return {'name': name }

    @classmethod
    def visit_class_alias(cls, node, children):
        """ ',' SP+ acword """
        return { 'alias': children[0] }

    @classmethod
    def visit_import(cls, node, children):
        """ SP+ '<import:' icaps_name '>' """
        d = {'import': children[0]}
        return d

    @classmethod
    def visit_class_header(cls, node, children):
        """Beginning of class section, includes name, optional class_alias and optional import marker"""
        items = {k: v for d in children for k, v in d.items()}
        return items

    @classmethod
    def visit_ee_header(cls, node, children):
        """
        "ee" name
        """
        return children[0]

    # Attributes
    @classmethod
    def visit_attr_block(cls, node, children):
        """ attr_header attribute+ """
        return {"attributes": children}

    @classmethod
    def visit_attribute(cls, node, children):
        """ INDENT attr_name (' : ' type_name)? (SP attr_tags)? EOL """
        items = {k: v for d in children for k, v in d.items()}
        return items

    @classmethod
    def visit_attr_name(cls, node, children):
        """ icaps_name """
        name = ''.join(children)
        return {'name': name }

    @classmethod
    def visit_type_name(cls, node, children):
        """ icaps_name """
        name = ''.join(children)
        return {'type': name }

    @classmethod
    def visit_attr_tags(cls, node, children):
        """ '{' attr_tag (',' SP attr_tag )* '}' """
        tdict = {}  # Tag dictionary of value lists per tag
        for tag in ['I', 'R', 'OR']:  # Identifier and referential attr tags
            tdict[tag] = [c[tag] for c in children if tag in c]  # Create list of values per tag from children
        return tdict

    @classmethod
    def visit_attr_tag(cls, node, children):
        """
        itag / rtag

        Beginning of class section, includes name, optional alias and optional import marker
        """
        item = children[0]
        return item

    @classmethod
    def visit_rtag(cls, node, children):
        """
       'O'? 'R' ordinal 'c'?

       Referential attribute tag

        Here we expect examples like these:
            R21c
            R22
            OR23

        The trick is to extract the number, conditionality status, and either R or OR
        """
        # 'R' gets swallowed by the parser since it is a literal, but 'O' shows up as a child
        # element for some reason. Not sure why 'O' is treated differently, but this complicates
        # the code below. Best solution is to clean up the grammar eventually.
        tag = 'OR' if node[0].value == 'O' else 'R'
        rnum = int(children.results['ordinal'][0])
        constraint = children[-1] == 'c'
        rtag = {tag: (rnum, constraint) }
        return rtag

    @classmethod
    def visit_itag(cls, node, children):
        """ '*'? 'I' ordinal? """
        itag = None
        if not children:
            itag = ID_a(1, False)
        else:
            super = True if children[0] == '*' else False
            tag_num = children[0] if not super else children[1]
            itag = ID_a(int(tag_num), super)
        id = {'I': itag }
        return id

    # Relationships
    @classmethod
    def visit_rel_section(cls, node, children):
        """ relationship_header rel* """
        return children

    @classmethod
    def visit_rel(cls, node, children):
        """ rname (ordinal_rel / binary_rel / gen_rel) block_end """
        return {**children[0], **children[1]}

    @classmethod
    def visit_rname(cls, node, children):
        """ INDENT rnum EOL """
        return {"rnum": children[0]}

    # Ordinal relationship
    @classmethod
    def visit_ordinal_rel (cls, node, children):
        """ ascend oform """
        items = {k: v for d in children for k, v in d.items()}
        return items

    @classmethod
    def visit_ascend(cls, node, children):
        """ INDENT highval SP '/' SP lowval ',' SP class_name EOL """
        items = {node.rule_name: {"highval": children[0], "lowval": children[1], "cname": children[2]['name']}}
        return items

    @classmethod
    def visit_highval(cls, node, children):
        """ phrase """
        return ''.join(children)

    @classmethod
    def visit_lowval(cls, node, children):
        """ phrase """
        return ''.join(children)

    @classmethod
    def visit_oform(cls, node, children):
        """ INDENT rank_attr SP ':' SP itag EOL """
        items = {node.rule_name: {"ranking attr": children[0], "id": children[1]['I'].number}}
        return items

    # Binary association
    @classmethod
    def visit_binary_rel(cls, node, children):
        """ t_side p_side assoc_class? ref1 ref2? """
        items = {k: v for d in children for k, v in d.items()}
        return items

    @classmethod
    def visit_t_side(cls, node, children):
        """ rel_side """
        items = {node.rule_name: {"phrase": children[0], "mult": children[1], "cname": children[2]}}
        return items

    @classmethod
    def visit_p_side(cls, node, children):
        """ rel_side """
        items = {node.rule_name: {"phrase": children[0], "mult": children[1], "cname": children[2]}}
        return items

    @classmethod
    def visit_phrase(cls, node, children):
        """ lword (delim lword)* """
        phrase = ''.join(children)
        return phrase

    @classmethod
    def visit_mult(cls, node, children):
        """ r'[1M]c?' """
        mult = node.value  # No children because literal 1 or M is thrown out
        return mult

    @classmethod
    def visit_assoc_class(cls, node, children):
        """ INDENT ('1' / 'M') SP+ icaps_name EOL """
        items = { "assoc_mult": children[0], "assoc_cname": children[1] }
        return items

    @classmethod
    def visit_binref(cls, node, children):
        """ INDENT source_attrs SP '->' SP target_attrs (',' SP itag)? EOL """
        id = 1 if len(children) < 3 else children[2]['I']  # referenced model identifier, default is I1
        ref = {'source': children[0], 'target': children[1], 'id': id}
        return ref

    @classmethod
    def visit_ref1(cls, node, children):
        """ binref """
        id = 1 if len(children) < 3 else children[2]['I']  # referenced model identifier, default is I1
        ref = { 'ref1': {'source': children[0], 'target': children[1], 'id': id}}
        return ref

    @classmethod
    def visit_ref2(cls, node, children):
        """ binref """
        id = 1 if len(children) < 3 else children[2]['I']  # referenced model identifier, default is I1
        ref = { 'ref2': {'source': children[0], 'target': children[1], 'id': id}}
        return ref

    # Generalization
    @classmethod
    def visit_gen_rel(cls, node, children):
        """ superclass subclasses genref """
        items = {k: v for d in children[1:] for k, v in d.items()}
        items["superclass"] = children[0]
        return items

    @classmethod
    def visit_superclass(cls, node, children):
        """ INDENT icaps_name SP? "+" EOL """
        return children[0]

    @classmethod
    def visit_subclasses(cls, node, children):
        """ subclass+ """
        return { 'subclasses': children }

    @classmethod
    def visit_subclass(cls, node, children):
        """ INDENT INDENT icaps_name EOL """
        return children[0]

    @classmethod
    def visit_genref(cls, node, children):
        """ single_line_genref """
        genrefs = {'genrefs': children}
        return genrefs

    @classmethod
    def visit_single_line_genref(cls, node, children):
        """ INDENT allsubs_attrs SP '->' SP target_attrs (',' SP itag)? EOL """
        id = 1 if len(children) < 3 else children[2]['I']  # referenced model identifier, default is I1
        grefs = {'source': children[0], 'target': children[1], 'id': id}
        return grefs

    @classmethod
    def visit_source_attrs(cls, node, children):
        """ single_class_attrs """
        class_name = children[0]['name']
        attrs = children[1]
        items = {'class': class_name, 'attrs': attrs}
        return items

    @classmethod
    def visit_target_attrs(cls, node, children):
        """ single_class_attrs """
        class_name = children[0]['name']
        attrs = children[1]
        items = {'class': class_name, 'attrs': attrs}
        return items

    @classmethod
    def visit_allsubs_attrs(cls, node, children):
        """ '<subclass>' attr_set """
        items = { 'class': '<subclass>', 'attrs': children[0]}
        return items

    @classmethod
    def visit_single_class_attrs(cls, node, children):
        """ class_name attr_set """
        items = { 'class': children[0], 'attrs': children[1]}
        return items

    @classmethod
    def visit_attr_set(cls, node, children):
        """ '.' ('(' attr_name (',' SP attr_name)+ ')' """
        attrs = [c['name'] for c in children]
        return attrs

    # Text and delimiters
    @classmethod
    def visit_acword(cls, node, children):
        """ r'[A-Z][A-Z0-9_]*' """
        return node.value  # No children since this is a literal

    @classmethod
    def visit_acaps_name(cls, node, children):
        """ acword (delim acword)* """
        name = ''.join(children)
        return name

    @classmethod
    def visit_icaps_all_name(cls, node, children):
        """ iword (delim iword)* """
        name = ''.join(children)
        return name

    @classmethod
    def visit_icaps_name(cls, node, children):
        """
        word (delim word)*
        """
        name = ''.join(children)
        return name

    # Discarded whitespace and comments
    @classmethod
    def visit_LINEWRAP(cls, node, children):
        """
        EOL SP*
        end of line followed by optional INDENT on next line
        """
        return None

    @classmethod
    def visit_EOL(cls, node, children):
        """
        SP* COMMENT? '\n'

        end of line: Spaces, Comments, blank lines, whitespace we can omit from the parser result
        """
        return None

    @classmethod
    def visit_SP(cls, node, children):
        """ ' '  Single space character (SP) """
        return None
