ISLR Sale and Purchase Functionalities
======================================


Due to the Dependendy reduction on the l10n_ve_withholding_islr module, it was
necessary to incorporate the functionalities regarding with the eliminated
dependencies on another module.

Because of that this module was created. This module adds the withholding
income concept to the sale and purchase orders. It moves the withholding income
concept defined in from the sale order to the stock, and, if the invoice was
created from the stock, it moves the withholding income concept to the
invoice. This also works the same way for purchase orders.
