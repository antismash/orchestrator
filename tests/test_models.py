import pytest
from mockaioredis import MockRedis

from orchestrator.models import Job

@pytest.fixture
def db():
    return MockRedis(encoding='utf-8')


@pytest.mark.asyncio
async def test_job_init(db):
    id_ = 'bacterial-1234-5678'
    job = Job(db, id_)
    assert job._id == id_
    assert job._key == 'aso:job:{}'.format(id_)
    assert job._taxon == 'bacterial'

    assert job.job_id == id_
    assert job.taxon == 'bacterial'

    await job.commit()

    db_job = await db.hgetall(job._key)
    expected = {
        'genefinding': 'none',
        'molecule_type': 'nucleotide',
        'state': 'created',
        'status': 'Awaiting processing',
    }
    assert db_job == expected



@pytest.mark.asyncio
async def test_job_accession(db):
    id_ = 'bacterial-1234-5678'
    job = Job(db, id_)

    job.accession = 'ABC1234'
    await job.commit()
    job.accession = 'broken'
    await job.fetch()

    assert job.accession == 'ABC1234'


@pytest.mark.asyncio
async def test_job_bools(db):
    id_ = 'bacterial-1234-5678'
    job = Job(db, id_)

    job.asf = True
    job.smcogs = False

    await job.commit()
    assert await db.hget(job._key, 'asf') == 'True'
    assert await db.hget(job._key, 'smcogs') == 'False'

    job.asf = None
    job.smcogs = None
    await job.fetch()

    assert job.asf
    assert job.smcogs == False


@pytest.mark.asyncio
async def test_job_ints(db):
    id_ = 'bacterial-1234-5678'
    job = Job(db, id_)

    job.seed = 1234

    await job.commit()
    assert await db.hget(job._key, 'seed') == '1234'

    job.seed = 0
    await job.fetch()

    assert job.seed == 1234


@pytest.mark.asyncio
async def test_job_floats(db):
    id_ = 'bacterial-1234-5678'
    job = Job(db, id_)

    job.cf_threshold = 0.2

    await job.commit()
    assert await db.hget(job._key, 'cf_threshold') == '0.2'

    job.cf_threshold = None
    await job.fetch()

    assert job.cf_threshold == 0.2


def test_job_state():
    id_ = 'bacterial-1234-5678'
    job = Job(None, id_)
    with pytest.raises(ValueError):
        job.state = 'invalid'


def test_job_molecule_type():
    id_ = 'bacterial-1234-5678'
    job = Job(None, id_)
    with pytest.raises(ValueError):
        job.molecule_type = 'invalid'


def test_job_genefinding():
    id_ = 'bacterial-1234-5678'
    job = Job(None, id_)
    with pytest.raises(ValueError):
        job.genefinding = 'invalid'


def test_job_valid_taxon():
    assert Job.is_valid_taxon('bacterial')
    assert Job.is_valid_taxon('fungal')
    assert Job.is_valid_taxon('plant')
    assert Job.is_valid_taxon('invalid') == False


def test_job_str():
    id_ = 'bacterial-1234-5678'
    job = Job(None, id_)
    assert str(job) == 'Job(id: bacterial-1234-5678, state: created)'


def test_job_from_dict():
    data = {
        'taxon': 'bacterial',
        'email': 'test@example.com',
        'smcogs': True,
        'asf': False,
        'genefinding': 'prodigal',
        'accession': 'AB12345',
        'molecule_type': 'nucleotide',
    }
    job = Job.from_dict(None, data)

    assert job.state == 'created'
    for key in data.keys():
        assert getattr(job, key) == data[key]


    data['taxon'] = 'invalid'
    with pytest.raises(ValueError):
        Job.from_dict(None, data)


def test_job_to_dict():
    data = {
        'taxon': 'bacterial',
        'email': 'test@example.com',
        'smcogs': True,
        'asf': False,
        'genefinding': 'prodigal',
        'accession': 'AB12345',
        'molecule_type': 'nucleotide',
    }
    job = Job.from_dict(None, data)

    data['job_id'] = job.job_id
    data['state'] = 'created'
    data['status'] = 'Awaiting processing'

    res = job.to_dict(extra_info=True)

    assert res == data


@pytest.mark.asyncio
async def test_job_fetch(db):
    id_ = 'bacterial-1234-5678'
    job = Job(db, id_)

    with pytest.raises(ValueError):
        await job.fetch()

    await job.commit()
    await job.fetch()
