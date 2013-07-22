Release notes for chevah.utils
==============================


0.19.4 - 22/07/2013
-------------------

* Removed redundant code from the message when generating SSH key.


0.19.3 - 19/07/2013
-------------------

* Added a more user friendly message when generating SSH key and no
  comment is specified.


0.19.2 - 18/07/2013
-------------------

* Added missing space in SSH key generation command line message.


0.19.1 - 17/07/2013
-------------------

* Bump version of minor review changes.


0.19.0 - 15/07/2013
-------------------

* Added possibility to specify a comment to a generated ssh key file.


0.18.0 - 07/06/2013
-------------------

* `_Logger`: Notify adding and removing of handlers.
* Add dynamic names for added handler.


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
