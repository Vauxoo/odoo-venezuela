# module_name/__terp__.py
{
    'name' : 'Cities Venezuela',
    'version' : '0.1',
    'author' : 'Vauxoo',
    'website' : 'http://wiki.openerp.org.ve/index.php?title=Boceto_estados_municipios',
    'category' : 'Localisation/Venezuela',
    'description' : 
    '''
    This Module only load Venezuela's Cities on object res.country.city
    Este Módulo solo carga las Ciudades de venezuela en la base de datos llenando el objeto res.country.city
    ''',
    'depends' : ['base','l10n_ve_states'],
    'init_xml' : [],
    'demo_xml' : [],
    'update_xml' : [
        'l10n_cities_ve_view.xml', 
        'l10n_cities_ve_data.xml',
        'country_view.xml',
        'partner_view.xml'
    ],
    'installable' : True,
    'active' : False,
}

