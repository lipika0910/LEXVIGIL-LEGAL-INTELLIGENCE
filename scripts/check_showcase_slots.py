"""Live synthetic lease check; remove only records/tokens created here."""
import json
from uuid import uuid4
from backend.hosted_connections import create_hosted_transactions
from backend.hosted_reports import HostedReports, ShowcaseCapacityExceeded
from backend.showcase_slots import ShowcaseSlots
from scripts.provision_hosted_logins import load_bundle, CA


def main():
    db = create_hosted_transactions(load_bundle(), CA)
    slots, reports = ShowcaseSlots(db), HostedReports(db)
    tokens = []
    owner = 'supabase:' + str(uuid4())
    aid = None
    try:
        for _ in range(4):
            tokens.append(slots.acquire())
        aid = reports.create(owner, 'Synthetic compute-lease deletion test')
        reports.delete(owner, aid)
        aid = None
        try:
            slots.acquire()
        except ShowcaseCapacityExceeded:
            pass
        else:
            raise AssertionError('Report deletion freed an independent compute slot')
        slots.release(tokens.pop())
        tokens.append(slots.acquire())
        # A token with the wrong value cannot release another request's lease.
        slots.release('0' * 64)
        try:
            slots.acquire()
        except ShowcaseCapacityExceeded:
            pass
        else:
            raise AssertionError('Unknown-token release altered occupancy')
        print(json.dumps({'slots':'passed','fifth_denied':True,
            'report_deletion_preserves_lease':True,'release_and_reacquire':True,
            'unknown_token_no_effect':True}))
    finally:
        try:
            for token in tokens:
                slots.release(token)
            if aid is not None:
                reports.delete(owner, aid)
        finally:
            for engine in db.engines.values():
                engine.dispose()


if __name__ == '__main__':
    try:
        main()
    except Exception as exc:
        print(json.dumps({'status':'failed','error_type':type(exc).__name__}))
        raise SystemExit(1) from None
