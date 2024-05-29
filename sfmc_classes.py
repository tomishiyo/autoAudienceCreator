class Folder:
    """
    A folder object in SFMC.

    :ivar id_code: (int) The folder's identifier in SFMC.
    :ivar parent_id: (int) The folder's parent identifier in SFMC.

    """
    def __init__(self, id_code, parent_id):
        """
        Initializes the Folder object.
        :param id_code: The folder's identifier in SFMC.
        :type id_code: int
        :param parent_id: The folder's parent identifier in SFMC.
        :type parent_id: int
        """
        self.id_code = id_code
        self.parent_id = parent_id


class DataExtension:
    """
    A data extension object in SFMC.

    :ivar id_code: (int) The de's identifier in SFMC. Same as External Key.
    :ivar parent_id: (int) The de's folder identifier in SFMC.
    """
    def __init__(self, object_id, parent_folder_id):
        """
        Initializes the Folder object.
        :param id_code: The de's identifier in SFMC. Same as External Key.
        :type id_code: int
        :param parent_id: The de's folder identifier in SFMC.
        :type parent_id: int
        """
        self.object_id = object_id
        self.parent_folder_id = parent_folder_id