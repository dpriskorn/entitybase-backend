# REDIRECT CREATE PROCESS

[RedirectHandler - redirect.py]
+--> Validate Request: redirect_from_id != redirect_to_id
+--> Check Entities Exist: redirect_from and redirect_to exist, not deleted/archived
+--> Get Head Revisions: from_head = vitess.get_head(redirect_from_id), to_head = vitess.get_head(redirect_to_id)
+--> Prepare Redirect Revision: revision_id = from_head + 1, data = {"redirects_to": redirect_to_id, "id": redirect_from_id}
+--> Store Revision: s3.write_entity_revision(redirect_from_id, revision_id, data)
+--> Update Entity Head: vitess.set_redirect_target(redirect_from_id, redirect_to_id)
+--> Insert Redirect Record: vitess.create_redirect(redirect_from_id, redirect_to_id, revision_id)
+--> Publish Event: stream_producer.publish_redirect_event(redirect_from_id, redirect_to_id, revision_id)
+--> Return Success

# REDIRECT REVERT PROCESS

[RedirectHandler - redirect.py]
+--> Validate Entity is Redirect: current_redirect_target = vitess.get_redirect_target(entity_id) != None
+--> Get Revert Revision: revert_to_revision_id (from request or previous)
+--> Fetch Revision Data: data = s3.get_entity_revision(entity_id, revert_to_revision_id)
+--> Update Revision Data: data["redirects_to"] = None
+--> Store Updated Revision: s3.write_entity_revision(entity_id, new_revision_id, data)
+--> Clear Redirect: vitess.set_redirect_target(entity_id, None)
+--> Publish Revert Event: stream_producer.publish_revert_event(entity_id, new_revision_id)
+--> Return Success