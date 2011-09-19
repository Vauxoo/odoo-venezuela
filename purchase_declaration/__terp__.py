{
  'name' : "Purchase & Sales Declaration Report",
  'version' : '1.0',
  'description' : """Purchase & Sales Declaration Report a.k.a Libros de Compras y Ventas
 This module allows to generate reports from the different periods of the fiscal year, in order
 to be presented to Venezuelan Authority (SENIAT),  According to the information provided in the official
 website: Doctrina y Jurisprudencia
 (http://www.seniat.gob.ve/portal/page/portal/MANEJADOR_CONTENIDO_SENIAT/02NORMATIVA_LEGAL/2.6DOCTRINA)
 referring to 'Log of to-tax operations with different taxes':
 Número de Consulta: 38895
 Materia: Deberes Formales
 Tema: Registro de operaciones gravadas con diferentes alícuotas.
 http://www.seniat.gob.ve/portal/page/portal/MANEJADOR_CONTENIDO_SENIAT/02NORMATIVA_LEGAL/2.6DOCTRINA/CRITERIOS_IVA_06_REGISTRO_DIFERENTES_ALICUOTAS.pdf
 the core of the information comes from:
 Reglamento de la Ley que Establece el Impuesto al Valor Agregado, en sus artículos 75 y 76
  """,
  'update_xml' : ['purchase_declaration_view.xml'],
  'init_xml' : [],
  'demo_xml' : [],
  # This line is used to bring in other Open ERP modules
  # You can leave a trailing ',' inside the list to make it easier when you're adding other modules later
  'depends' : ['account',],
  'installable' : True,
  'active' : False,
  # This line would be 'Profiles' to enable it to appear with other profiles during installation
  'category' : 'Generic Modules/Purchase',
  'author' : 'Vauxoo',
  'website' : 'http://openerp.com.ve',
}
