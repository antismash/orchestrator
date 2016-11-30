'Datatypes that hit the Redis DB'
import logging
import uuid


class Job:
    VALID_TAXA = {'bacterial', 'fungal', 'plant'}
    PROPERTIES = ['state', 'molecule_type', 'genefinding']
    ATTRIBUTES = [
        'accession',
        'seqfile',
        'annfile',
        'email',
        'status',
        'clusterblast',
        'subclusterblast',
        'knownclusterblast',
        'smcogs',
        'asf',
        'clusterfinder',
        'borderpredict',
        'full_hmmer',
        'seed',
        'cf_cdsnr',
        'cf_threshold',
        'cf_npfams',
    ]

    BOOL_ARGS = {
        'clusterblast',
        'subclusterblast',
        'knownclusterblast',
        'smcogs',
        'asf',
        'clusterfinder',
        'borderpredict',
        'full_hmmer',
    }

    INT_ARGS = {
        'seed',
        'cf_cdsnr',
        'cf_npfams',
    }

    FLOAT_ARGS = {
        'cf_threshold',
    }


    def __init__(self, db, job_id):
        self._db = db
        self._id = job_id
        self._key = 'aso:job:{}'.format(self._id)

        # taxon is the first element of the ID
        self._taxon = self._id.split('-')[0]

        # storage for properties
        self._state = 'created'
        self._molecule_type = 'nucleotide'
        self._genefinding = 'none'


        for attribute in self.ATTRIBUTES:
            setattr(self, attribute, None)

        # Regular attributes that differ from None
        self.status = 'Awaiting processing'


    # Not really async, but follow the same API as the other properties
    @property
    def job_id(self):
        return self._id

    # No setter, job_id is a read-only property

    # Not really async, but follow same API as the other properties
    @property
    def taxon(self):
        return self._taxon

    # No setter, taxon is a read-only property


    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, value):
        if value not in {
            'created',
            'downloading',
            'validating',
            'running',
            'done',
            'failed'}:
            raise ValueError('Invalid state')

        self._state = value


    @property
    def molecule_type(self):
        return self._molecule_type

    @molecule_type.setter
    def molecule_type(self, value):
        if value not in {'nucleotide', 'protein'}:
            raise ValueError('Invalid molecule_type')

        self._molecule_type = value


    @property
    def genefinding(self):
        return self._genefinding

    @genefinding.setter
    def genefinding(self, value):
        if value not in {'prodigal', 'prodigal-m', 'none'}:
            raise ValueError('Invalid genefinding method')
        self._genefinding = value


    @staticmethod
    def is_valid_taxon(taxon: str) -> bool:
        '''
        Check if taxon string is one of 'bacterial', 'fungal' or 'plant'
        '''
        if taxon not in Job.VALID_TAXA:
            return False

        return True


    @classmethod
    def from_dict(cls, db, data):

        taxon = data.get('taxon', '')
        if not Job.is_valid_taxon(taxon):
            raise ValueError("Invalid taxon {!r}, needs to be one of ".format(taxon, Job.VALID_TAXA))

        job_id = '{}-{}'.format(taxon, uuid.uuid4())

        cls = Job(db, job_id)

        args = cls.PROPERTIES + cls.ATTRIBUTES

        for arg in args:
            val = data.get(arg, None)
            if val is None:
                continue
            setattr(cls, arg, val)

        return cls


    def to_dict(self):
        ret = {}

        args = self.PROPERTIES + self.ATTRIBUTES

        for arg in args:
            if getattr(self, arg) is not None:
                ret[arg] = getattr(self, arg)

        return ret

    def __str__(self):
        return "Job(id: {}, state: {})".format(self._id, self.state)


    async def fetch(self):
        args = self.PROPERTIES + self.ATTRIBUTES

        values = await self._db.hmget(self._key, args)


        for i, arg in enumerate(args):
            val = values[i]

            if val is None:
                continue

            if arg in self.BOOL_ARGS:
                val = (val != 'False')
            elif arg in self.INT_ARGS:
                val = int(val)
            elif arg in self.FLOAT_ARGS:
                val = float(val)

            setattr(self, arg, val)


    async def commit(self):
        return await self._db.hmset_dict(self._key, self.to_dict())
