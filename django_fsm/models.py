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

    field = models.CharField(max_length=64,
            verbose_name='Model field')

    name = models.CharField(max_length=64,
            verbose_name='Function name')

    source = models.CharField(max_length=50,
            verbose_name='Previous state')
    
    target = models.CharField(max_length=50,
            verbose_name='New state')

    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    
    content_object = generic.GenericForeignKey('content_type', 'object_id')
    
    @property
    def qualified_field(self):
        return "%s.%s" % (self.content_type, self.field)

    def __unicode__(self):
        return u"%s.%s '%s' => '%s'" % (
                self.content_type,
                self.field,
                self.source,
                self.target)

    def __repr__(self):
        return "Audit(%s, '%s' => '%s')" \
                % (repr(self.content_object), self.source, self.target)

class AuditManager(models.Manager):
    """
    The `AuditManager` provides a manager than can be limited to a
    particular ContentType and field.
    """
    def __init__(self, instance, cls, field, *args, **kwargs):
        self._cls = cls
        self._field = field
        self._instance = instance
        super(AuditManager, self).__init__(*args, **kwargs)
        
        self.model = Audit

    def get_query_set(self):
        content_type = ContentType.objects.get_for_model(self._cls)
        return super(AuditManager, self).get_query_set().filter(content_type__pk=content_type.id,
                field=self._field,
                object_id=self._instance.id)


@receiver(signals.post_transition)
def log_transition(sender, **kwargs):
    """
    The signal handler, `log_transition`, creates an audit log
    entry on `post_transition`.

    This allow us to keep an audit trail for state changes.
    """
    instance = kwargs['instance']
    source = kwargs['source']
    target = kwargs['target']
    field = kwargs['field']
    name = kwargs['name']
    
    audit = Audit(field=field,
            source=source,
            target=target,
            name=name,
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

