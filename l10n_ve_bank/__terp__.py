{
    "name" : "Managing Banks in Venezuela",
    "version" : "0.1",
    "depends" : ["account_voucher_payment","base"],
    "author" : "Vauxoo",
    "description" : """
    What do this module:
        Load the list of banks en Venezuela.
        Enable admin Checks and talonaries of checks, by bank account and partner.
        Enable print Checks with several templates pre - loaded, and related to bank accounts.
        Relate all payments with check to an specific account an an specific check number, 
                    """,
    "website" : "http://openerp.com.ve",
    "category" : "Generic Modules/Accounting",
    "init_xml" : [
    ],
    "demo_xml" : [
    ],
    "update_xml" : [
        "data/res.bank.xml",
    ],
    "active": False,
    "installable": True,
}
