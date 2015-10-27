Venezuelan Fiscal Requirements
==============================


- Invoice Control Number.
- Tax*except concept, necesary rule by Venezuelan Laws.
- Required address invoice.
- Unique billing address (invoice), necesary rule by Venezuelan Laws.
- VAT verification for Venezuela rules.
- If you have internet conexion you will be able of update your partner
  information from SENIAT Automatically on install wizard.
- Damaged "Legal free forms" declaration.
- Tax Units configuration.
- When a partner is updated by using the SENIAT Update Button, its name changes
  to readonly to avoid manual changes.
- Add field Parent in the invoice of customers and suppliers, for link the
  invoice  that generated debit or credit note.

    -  Add wizard for generate debit note from invoice and done accounting
       entry.
    -  Add wizard to assign, modify or unlink source invoice (parent invoice)
       to another one.
    -  Automatically unreconciles paid invoices when making a refund of type
       modify or cancel.
    -  Validate automatically the withholding of debit notes.
    -  Add a field on taxes configuration form for indicating the type of tax
       according to venezuelan laws

For damaged invoices (Free form formats), you must go to the company and, under
the configuration section, create the corresponding journal and account.

TODO Include this on wizard configuration.

If you install this module with invoice data on the database, the concept_id
will be Empty for all those invoices, so, when you try to modify them you
have to add a value on that field

This module should also install a menu item under the accounting configuration
menu.

We now have a configuration wizard after this module install.

You will need some extra modules:
  * debit_credit_note

Custom modules can be found in the following branch:
  * Addons-vauxoo: lp:addons-vauxoo/7.0