{
    'name': 'Pago de nóminas',
    'version': '1.2',
    'description': '',
    'summary': '',
    'author': 'Jhon Jairo Rojas Ortiz',
    'website': '',
    'license': 'LGPL-3',
    'category': '',
    'depends': [
        'account', 'base', 'account_payment_flow', 'purchase', 'base_setup', 'hr_expense', 'l10n_latam_invoice_document'
    ],
    'data': [
        'data/ir_sequence.xml',
        'data/payroll_payment_type.xml',
        'data/res_groups.xml',
        'data/ir_ui_menu.xml',
        'security/ir.model.access.csv',
        'wizards/payroll_payment_wizard_views.xml',
        'wizards/warning_views.xml',
        'wizards/account_move_observation_views.xml',
        'wizards/assign_flow_group_views.xml',
        'views/res_partner_views.xml',
        'views/account_move_views.xml',
        'views/account_payment_views.xml',
        'views/res_bank_views.xml',
        'views/payroll_payment_views.xml',
        'views/hr_expense_views.xml',
        'views/payroll_payment_type_views.xml',
        # 'views/res_config_settings_views.xml',
    ],
    'demo': [

    ],
    'auto_install': False,
    'application': False,
    'assets': {

    }
}
