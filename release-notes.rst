Release notes for chevah.utils
==============================


0.17.0 - 06/06/2013
-------------------

* Notify changes in LogConfigurationSection for `file`, 'syslog' and
  `windows_eventlog`.


0.16.0 - 05/06/2013
-------------------

* Add FileConfigurationProxy.isDisabledValue().
* Allow saving LogConfigurationSection.log_rotate_each using the same
  format returned by it.


0.15.0 - 24/05/2013
-------------------

* Make `_IWithPropertiesMixin` public interface and rename it to
  `IPropertyMixin`.
* `WithConfigurationPropertyMixin` renamed to
  `PropertiesMixin`.


0.14.0 - 22/05/2013
-------------------

* Remove interpolation for configuration file. Read and write raw
  configuration file.
