from openerp.tests.common import TransactionCase


class MenuItemCase(TransactionCase):
    """
    Common setup for testing menu items
    """

    def get_groups_for_menu_item(self, menu_item_name):
        """
        Get the menu item with the supplied name and return the names of the
        groups that can see it

        :param menu_item_name: Name of the menu item to get
        :return: list of group names
        """
        menu_model = self.env['ir.ui.menu']
        recently_discharged_item = menu_model.search(
            [
                ['name', '=', menu_item_name]
            ]
        )
        return [group.name for group in recently_discharged_item.groups_id]
