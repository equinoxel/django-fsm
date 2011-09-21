from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic

from django_fsm import signals
from django.dispatch import receiver


class Audit(models.Model):
    """
    The `Audit` model stores information about state transitions.
    """

    created_at = models.DateTimeField(auto_now_add=True,
            help_text='Date and time of state change')

    field = models.CharField(max_length=32,
            verbose_name='Model field')

    source = models.CharField(max_length=50,
            verbose_name='Previous state')
    
    target = models.CharField(max_length=50,
            verbose_name='New state')

    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    
    content_object = generic.GenericForeignKey('content_type', 'object_id')


    def __repr__(self):
        return "Audit(%s, '%s' => '%s')" \
                % (repr(self.content_object), self.source, self.target)



@receiver(signals.post_transition)
def log_transition(sender, **kwargs):
    """
    The signal handler, `log_transition`, creates an audit log
    entry when on `post_transition`.

    This allow us to keep an audit trail for state changes.
    """
    instance = kwargs['instance']
    source = kwargs['source']
    target = kwargs['target']
    field = kwargs['field']
    
    audit = Audit(field=field,
            source=source,
            target=target,
            content_object=instance)

    if hasattr(instance, '_django_fsm_audits'):
        instance._django_fsm_audits.append(audit)
    else:
        instance._django_fsm_audits = [audit]

@receiver(models.signals.post_save)
def save_model_audits(sender, **kwargs):
    """
    The signal handler, `save_model_audits`, saves the audit logs
    when the original model is saved.
    """
    instance = kwargs['instance']

    if hasattr(instance, '_django_fsm_audits'):
        for audit in instance._django_fsm_audits:
            audit.save()

