# Kubernetes Cluster Requirements for New Backend

I estimated the requirements for the Kubernetes cluster running my new backend. 😀  
This is ChatGPT recommendations based on my requirements:  

This setup supports:  

- **500M entities + 500M statements + 7M statements/day**  
- This equals **700k new item creations/day** and a total of **10 changes/sec**

> This is not a minimum. If you reduce the ingestion by rate limiting creation of new items to say max 3/sec, you can lower the Vitess requirements considerably.

---

Currently, Wikidata runs on a few clusters of quite beefy machines. The machines are expensive because everything has to be kept in RAM (this is true for both MariaDB master/slave and the current Blazegraph clusters).  

If WDQS goes ahead with QLever, they still need beefy machines for that because it is not cloud native AFAIK.  

But the current blob storage and MariaDB clusters can be reduced significantly once the entity data is offloaded to the new backend.  

The only thing left in MW are the wikipages, the users, and permissions — not much else.  

So much of the current hardware can be used in the cluster once the transition is done. You could start with a **hybrid cluster** where you rent machines in the public cloud first until the transition is done, then you add the old machines to your local Kubernetes cluster and buy until you have no hybrid left and run fully locally.

---

## Detailed Pod/Resource Estimates

| Component | Pods | CPU | RAM | Notes |
|-----------|------|-----|-----|-------|
| Vitess Tablets | 256–384 | 16–24 cores/pod | 64–128GB | 128 shards × 2–3 replicas |
| Streaming Workers | 50–100 | 4–8 cores | 16–32GB | Batch inserts, Kafka/Pulsar queue |
| REST API | 50–100 | 2–4 cores | 8–16GB | Autoscale with CPU / requests |
| Cache (Redis) | 50–100 | - | 64–128GB | Top 5–10M hot entities |
| Ceph OSD | 50–100 | - | - | SSD/HDD tiering, replication factor 3 |
| Ceph Monitor | 3 | - | - | HA |
| Dump Workers | 128 | 4–8 cores | 16–32GB | Rolling dumps |
| Nginx / LB | 10–20 | 4–8 cores | 8–16GB | Frontend, optional CDN |

---

## Total Cluster Resource Summary

| Resource | Total Estimate |
|----------|----------------|
| CPU cores | 5,000 – 6,000 |
| RAM | 20 – 30 TB |
| Hot storage (SSD) | ~500 TB |
| Cold storage (HDD / Ceph) | ~1 – 1.5 PB |
