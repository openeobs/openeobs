# Part of Open eObs. See LICENSE file for full copyright and licensing details.
from openerp.osv import orm


class res_users(orm.Model):
    _inherit = 'res.users'

    def init(self, cr):
        # MIGRATION FROM NON ROLE BASED DB
        category_pool = self.pool['res.partner.category']
        hca_cat_id = category_pool.search(
            cr, 1, [['name', '=', 'HCA']])[0]
        nur_cat_id = category_pool.search(
            cr, 1, [['name', '=', 'Nurse']])[0]
        wma_cat_id = category_pool.search(
            cr, 1, [['name', '=', 'Shift Coordinator']])[0]
        sma_cat_id = category_pool.search(
            cr, 1, [['name', '=', 'Senior Manager']])[0]
        doc_cat_id = category_pool.search(
            cr, 1, [['name', '=', 'Doctor']])[0]
        sdr_cat_id = category_pool.search(
            cr, 1, [['name', '=', 'Senior Doctor']])[0]
        jdr_cat_id = category_pool.search(
            cr, 1, [['name', '=', 'Junior Doctor']])[0]
        reg_cat_id = category_pool.search(
            cr, 1, [['name', '=', 'Registrar']])[0]
        con_cat_id = category_pool.search(
            cr, 1, [['name', '=', 'Consultant']])[0]
        rec_cat_id = category_pool.search(
            cr, 1, [['name', '=', 'Receptionist']])[0]
        adm_cat_id = category_pool.search(
            cr, 1, [['name', '=', 'System Administrator']])[0]
        kio_cat_id = category_pool.search(
            cr, 1, [['name', '=', 'Kiosk']])[0]
        roles = [
            hca_cat_id,
            nur_cat_id,
            wma_cat_id,
            sma_cat_id,
            doc_cat_id,
            sdr_cat_id,
            jdr_cat_id,
            reg_cat_id,
            con_cat_id,
            rec_cat_id,
            adm_cat_id,
            kio_cat_id
        ]
        migrate_users = self.search(
            cr, 1, [['category_id', 'not in', roles]])
        user_ids = self.search(
            cr, 1, [
                ['groups_id.name', 'in', ['NH Clinical HCA Group']],
                ['id', 'in', migrate_users]
            ]
        )
        self.write(cr, 1, user_ids, {'category_id': [[4, hca_cat_id]]})
        user_ids = self.search(
            cr, 1, [
                ['groups_id.name', 'in', ['NH Clinical Nurse Group']],
                ['id', 'in', migrate_users]
            ]
        )
        self.write(cr, 1, user_ids, {'category_id': [[4, nur_cat_id]]})
        user_ids = self.search(
            cr, 1, [
                ['groups_id.name', 'in', ['NH Clinical Shift Coordinator Group']],
                ['id', 'in', migrate_users]
            ]
        )
        self.write(cr, 1, user_ids, {'category_id': [[4, wma_cat_id]]})
        user_ids = self.search(
            cr, 1, [
                ['groups_id.name', 'in', ['NH Clinical Senior Manager Group']],
                ['id', 'in', migrate_users]
            ]
        )
        self.write(cr, 1, user_ids, {'category_id': [[4, sma_cat_id]]})
        user_ids = self.search(
            cr, 1, [
                ['groups_id.name', 'in', ['NH Clinical Doctor Group']],
                ['id', 'in', migrate_users]
            ]
        )
        for uid in user_ids:
            self.write(
                cr, 1, uid, {
                    'category_id': [
                        [4, doc_cat_id],
                        [3, sdr_cat_id],
                        [3, jdr_cat_id],
                        [3, reg_cat_id],
                        [3, con_cat_id]
                    ]
                }
            )
        user_ids = self.search(
            cr, 1, [
                ['groups_id.name', 'in', ['NH Clinical Admin Group']],
                ['id', 'in', migrate_users]
            ]
        )
        self.write(cr, 1, user_ids, {'category_id': [[4, adm_cat_id]]})
        user_ids = self.search(
            cr, 1, [
                ['groups_id.name', 'in', ['NH Clinical Kiosk Group']],
                ['id', 'in', migrate_users]
            ]
        )
        self.write(cr, 1, user_ids, {'category_id': [[4, kio_cat_id]]})
        user_ids = self.search(
            cr, 1, [
                ['groups_id.name', 'in', ['NH Clinical Senior Doctor Group']],
                ['id', 'in', migrate_users]
            ]
        )
        self.write(cr, 1, user_ids, {'category_id': [[4, sdr_cat_id]]})
        user_ids = self.search(
            cr, 1, [
                ['groups_id.name', 'in', ['NH Clinical Junior Doctor Group']],
                ['id', 'in', migrate_users]
            ]
        )
        self.write(cr, 1, user_ids, {'category_id': [[4, jdr_cat_id]]})
        user_ids = self.search(
            cr, 1, [
                ['groups_id.name', 'in', ['NH Clinical Registrar Group']],
                ['id', 'in', migrate_users]
            ]
        )
        self.write(cr, 1, user_ids, {'category_id': [[4, reg_cat_id]]})
        user_ids = self.search(
            cr, 1, [
                ['groups_id.name', 'in', ['NH Clinical Consultant Group']],
                ['id', 'in', migrate_users]
            ]
        )
        self.write(cr, 1, user_ids, {'category_id': [[4, con_cat_id]]})
        user_ids = self.search(
            cr, 1, [
                ['groups_id.name', 'in', ['NH Clinical Receptionist Group']],
                ['id', 'in', migrate_users]
            ]
        )
        self.write(cr, 1, user_ids, {'category_id': [[4, rec_cat_id]]})
        # END OF MIGRATION
        super(res_users, self).init(cr)
