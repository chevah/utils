Release notes for chevah.utils
==============================


0.18.0 - 07/06/2013
-------------------

* `_Logger`: Notify adding and removing of handlers.


0.17.1 - 07/06/2013
-------------------

* Notify changes in LogConfigurationSection for `file_rotate_external`,
  `file_roate_at_size`, `file_rotate_each`, `file_rotate_count`.
* When notification fails, revert configuration value.


0.17.0 - 06/06/2013
-------------------

* Notify changes in LogConfigurationSection for `file`, 'syslog' and
  `windows_eventlog`.
* Automatically reconfigure file, syslog and windows_eventlog.


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
