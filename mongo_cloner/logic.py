import os
import json
from pymongo import MongoClient, ReplaceOne
from bson import json_util

class MongoClonerLogic:
    def __init__(self, log_callback=None):
        self.log_callback = log_callback
        self.batch_size = 1000

    def _log(self, message):
        if self.log_callback:
            self.log_callback(message)
        else:
            print(message)

    def _clean_uri(self, uri):
        """Removes common typos from the URI like trailing dots."""
        # Simple handle for common "10.0.0.15.:27017"
        return uri.replace('.:', ':')

    def direct_clone(self, src_uri, src_db_name, dst_uri, dst_db_name):
        """Clones a database directly from one server to another using pymongo with upserts."""
        try:
            src_uri = self._clean_uri(src_uri)
            dst_uri = self._clean_uri(dst_uri)

            src_client = MongoClient(src_uri)
            dst_client = MongoClient(dst_uri)

            src_db = src_client[src_db_name]
            dst_db = dst_client[dst_db_name]

            self._log(f"Starting direct clone from {src_db_name} to {dst_db_name}")
            
            collections = src_db.list_collection_names()
            for coll_name in collections:
                # Skip system collections
                if coll_name.startswith("system."):
                    continue
                
                self._log(f"Cloning collection: {coll_name}")
                src_coll = src_db[coll_name]
                dst_coll = dst_db[coll_name]

                cursor = src_coll.find({})
                batch_ops = []
                count = 0
                for doc in cursor:
                    # Use upsert logic to avoid duplicate key errors
                    batch_ops.append(ReplaceOne({'_id': doc['_id']}, doc, upsert=True))
                    
                    if len(batch_ops) >= self.batch_size:
                        dst_coll.bulk_write(batch_ops, ordered=False)
                        count += len(batch_ops)
                        self._log(f"  Processed {count} documents (upserts)...")
                        batch_ops = []
                
                if batch_ops:
                    dst_coll.bulk_write(batch_ops, ordered=False)
                    count += len(batch_ops)
                    self._log(f"  Finished {coll_name} with {count} documents.")

            self._log("Direct clone completed successfully.")
            return 0
        except Exception as e:
            self._log(f"ERROR: {str(e)}")
            return 1

    def dump_to_file(self, uri, db_name, output_path):
        """Creates a dump of the database to JSON files."""
        try:
            uri = self._clean_uri(uri)
            client = MongoClient(uri)
            db = client[db_name]

            self._log(f"Dumping database {db_name} to {output_path}")
            if not os.path.exists(output_path):
                os.makedirs(output_path)
            
            collections = db.list_collection_names()
            for coll_name in collections:
                if coll_name.startswith("system."):
                    continue

                self._log(f"Exporting collection: {coll_name}")
                file_path = os.path.join(output_path, f"{coll_name}.json")
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    cursor = db[coll_name].find({})
                    for doc in cursor:
                        # Use json_util for BSON types
                        f.write(json.dumps(doc, default=json_util.default) + '\n')
            
            self._log("Dump completed successfully.")
            return 0
        except Exception as e:
            self._log(f"ERROR: {str(e)}")
            return 1

    def restore_from_file(self, uri, db_name, input_path):
        """Restores a database from JSON files using upserts."""
        try:
            uri = self._clean_uri(uri)
            client = MongoClient(uri)
            db = client[db_name]

            self._log(f"Restoring database {db_name} from {input_path}")
            
            if not os.path.isdir(input_path):
                self._log(f"ERROR: {input_path} is not a directory.")
                return 1

            for filename in os.listdir(input_path):
                if filename.endswith(".json"):
                    coll_name = filename[:-5]
                    self._log(f"Importing collection: {coll_name}")
                    
                    file_path = os.path.join(input_path, filename)
                    batch_ops = []
                    count = 0
                    
                    with open(file_path, 'r', encoding='utf-8') as f:
                        for line in f:
                            if not line.strip():
                                continue
                            doc = json.loads(line, object_hook=json_util.object_hook)
                            # Use upsert logic
                            batch_ops.append(ReplaceOne({'_id': doc['_id']}, doc, upsert=True))
                            
                            if len(batch_ops) >= self.batch_size:
                                db[coll_name].bulk_write(batch_ops, ordered=False)
                                count += len(batch_ops)
                                self._log(f"  Imported {count} documents (upserts)...")
                                batch_ops = []
                    
                    if batch_ops:
                        db[coll_name].bulk_write(batch_ops, ordered=False)
                        count += len(batch_ops)
                        self._log(f"  Finished {coll_name} with {count} documents.")

            self._log("Restore completed successfully.")
            return 0
        except Exception as e:
            self._log(f"ERROR: {str(e)}")
            return 1
