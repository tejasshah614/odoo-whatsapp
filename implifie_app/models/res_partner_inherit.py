from odoo import models
import logging

_logger = logging.getLogger(__name__)

class ResPartner(models.Model):
    _inherit = ['res.partner', 'base.model.extension']  # Inherit from both res.partner and abstract model

    def create(self, vals):
        _logger.info(f'Creating record with values: {vals}')
        record = super(ResPartner, self).create(vals)
        record._process_trigger_event('create')  # Trigger the event
        return record

    def write(self, vals):
        _logger.info(f'Updating record with values: {vals}')
        result = super(ResPartner, self).write(vals)
        self._process_trigger_event('write')  # Trigger the event
        return result

class StudentTest(models.Model):
    # _name = 'student.test'
    _inherit = ['student.test','base.model.extension']  # Inherit the base model extension
    
    def create(self, vals):
        _logger.info(f'Creating student record with values: {vals}')
        record = super(StudentTest, self).create(vals)
        record._process_trigger_event('create')  # Trigger the event
        return record

    def write(self, vals):
        _logger.info(f'Updating student record with values: {vals}')
        result = super(StudentTest, self).write(vals)
        self._process_trigger_event('write')  # Trigger the event
        return result

class CrmLead(models.Model):
    _inherit = ['crm.lead', 'base.model.extension']  # Inherit from crm.lead and base.model.extension

    def create(self, vals):
        _logger.info(f'Creating crm record with values: {vals}')
        # Corrected the super call to use CRMLead instead of StudentTest
        record = super(CrmLead, self).create(vals)
        record._process_trigger_event('create')  # Trigger the event
        return record

    def write(self, vals):
        _logger.info(f'Updating record with values: {vals}')
        # Corrected the super call to use CRMLead instead of StudentTest
        result = super(CrmLead, self).write(vals)
        self._process_trigger_event('write')  # Trigger the event
        return result

class SaleOrder(models.Model):
    _inherit = ['sale.order', 'base.model.extension']  # Inherit from crm.lead and base.model.extension

    def create(self, vals):
        _logger.info(f'Creating crm record with values: {vals}')
        # Corrected the super call to use CRMLead instead of StudentTest
        record = super(SaleOrder, self).create(vals)
        record._process_trigger_event('create')  # Trigger the event
        return record

    def write(self, vals):
        _logger.info(f'Updating record with values: {vals}')
        # Corrected the super call to use CRMLead instead of StudentTest
        result = super(SaleOrder, self).write(vals)
        self._process_trigger_event('write')  # Trigger the event
        return result

class AccountMove(models.Model):
    _inherit = ['account.move', 'base.model.extension']

    def create(self, vals):
        _logger.info(f'Creating AccountMove record with values: {vals}')
        record = super(AccountMove, self).create(vals)
        record._process_trigger_event('create')
        return record

    def write(self, vals):
        _logger.info(f'Updating AccountMove record with values: {vals}')
        result = super(AccountMove, self).write(vals)
        self._process_trigger_event('write')
        return result

class ProductTemplate(models.Model):
    _inherit = ['product.template', 'base.model.extension']

    def create(self, vals):
        _logger.info(f'Creating ProductTemplate record with values: {vals}')
        record = super(ProductTemplate, self).create(vals)
        record._process_trigger_event('create')
        return record

    def write(self, vals):
        _logger.info(f'Updating ProductTemplate record with values: {vals}')
        result = super(ProductTemplate, self).write(vals)
        self._process_trigger_event('write')
        return result


# class ProjectTask(models.Model):
#     _inherit = ['project.task', 'base.model.extension']

#     def create(self, vals):
#         _logger.info(f'Creating ProjectTask record with values: {vals}')
#         record = super(ProjectTask, self).create(vals)
#         record._process_trigger_event('create')
#         return record

#     def write(self, vals):
#         _logger.info(f'Updating ProjectTask record with values: {vals}')
#         result = super(ProjectTask, self).write(vals)
#         self._process_trigger_event('write')
#         return result




