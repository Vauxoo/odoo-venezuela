# module_name/__terp__.py
{
    'name' : 'Municipios Venezuela',
    'version' : '0.1',
    'author' : 'Vauxoo',
    'website' : 'http://wiki.openerp.org.ve/index.php?title=Boceto_estados_municipios',
    'category' : 'Localisation/Venezuela',
    'description' : 
'''
This Module only load Venezuela's municipalities on object res.country.state.municipalities
Este Módulo solo carga las Municipios de venezuela en la base de datos llenando el objeto res.country.state.municipalities
''',
    'depends' : ['base','l10n_ve_states','l10n_ve_cities'],
    'init_xml' : [],
    'demo_xml' : [],
    'update_xml' : [
        'l10n_ve_municipalities_view.xml', 
        'l10n_ve_municipalities_data.xml', 
        'country_view.xml', 
        'partner_view.xml'
    ],
    'installable' : True,
    'active' : False,
}

