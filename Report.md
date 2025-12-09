Assignment 5 Report
---------------------

# Team Members
Annabel Morgenstern
Torsten Schmälzle

# GitHub link to your (forked) repository

https://github.com/abibvm/Distributed_Systems_Assignment_5.git

# Task 1

Note: Some questions require you to take screenshots. In that case, please join the screenshots and indicate in your answer which image refer to which screenshot.

1. What happens when Raft starts? Explain the process of electing a leader in the first
term.

Ans: 

When a Raft cluster starts, all servers begin as followers with randomized election timeouts. The server whose timeout expires first becomes a candidate, votes for itself, and sends RequestVote messages to the others. Since no leader exists yet and no votes have been cast, the other servers grant their votes, giving the candidate a majority and allowing it to become the leader.
Once elected, the leader sends regular heartbeat messages to reset follower timeouts and prevent new elections. Raft needs this leader so that all client requests flow through a single node, ensuring log entries are replicated in order and stay consistent. Only a server with an up-to-date log can become leader, which helps Raft maintain correctness.


2. Perform one request on the leader, wait until the leader is committed by all servers. Pause the simulation.
Then perform a new request on the leader. Take a screenshot, stop the leader and then resume the simulation.
Once, there is a new leader, perform a new request and then resume the previous leader. Once, this new request is committed by all servers, pause the simulation and take a screenshot. Explain what happened?

Ans: 

When the first request is sent to the leader, it adds the operation to its log and replicates it to the followers. Once a majority have stored the entry, the leader commits it and applies the update. All servers eventually commit the same entry.
A second request is then made, but before it can be committed, the leader is paused. Since it stops sending heartbeats, the remaining servers hold an election, and the server with the shortest timeout becomes the new leader.
A client request is sent to this new leader, which appends the entry to its log and replicates it to the followers. Meanwhile, the paused leader still has an outdated log. When it is brought back online, its log conflicts with the current leader’s log. Raft resolves this by having the new leader backtrack until it finds a matching log index and then overwrite the conflicting entries on the old leader.
Once the corrected log entry has been replicated to a majority—including the restarted server—it becomes committed on all servers, and the cluster returns to a consistent state.



3. Using the same visualization, stop the current leader and two additional servers. After a few increments, pause the simulation and take a screenshot. Then resume all servers and restart the simulation. After the leader election, pause the simulation and take a screenshot. How do you explain the behavior of the system during the above exercise?

Ans: 

When I stopped the current leader together with two additional servers, the cluster was reduced to only two active nodes. With just two machines running, Raft can no longer reach a majority, because a leader needs at least three votes in a five-server cluster. As a result, both remaining servers kept timing out and starting new elections, but none of them could ever gather enough votes to become leader. This caused the term number to continue increasing without any leader being elected.

After resuming all the servers, the previously stopped machines rejoined the cluster. Once the system was fully running again, the first server whose election timeout expired immediately requested votes from the others. Because a majority was now available, it received enough votes, its term jumped ahead of the others, and it was elected the new leader. From that point on, the cluster stabilized again and S2 began sending out heartbeats to the followers.

# Task 2

1. Which server is the leader? Can there be multiple leaders? Justify your answer using the statuses from the different servers.
Ans: 

Based on the status responses of all three servers, it is clear that node3:6002 is the leader of the Raft cluster. Both node1 and node2 report that their Raft state is state: 0, which indicates that they are followers, 
and each of them lists "leader": TCPNode('node3:6002') as the current leader. The decisive confirmation comes from node3’s own status output:
it reports "self": TCPNode('node3:6002'), "leader": TCPNode('node3:6002'), and most importantly "state": 2, where state 2 represents the leader role in the Raft state machine.


2. Perform a PUT operation for the key "a" on the leader. Check the status of the different nodes. What changes have occurred and why (if any)?


Ans:

After performing a PUT operation on the leader for the key “a”, a new log entry was added to the Raft log and replicated to all nodes. This caused the log_len, commit_idx, and last_applied values to
increase on every server. These changes occur because a PUT operation is a write request, and Raft must record it in the log, replicate it to the followers, and commit it once a majority acknowledges it. 
As a result, all nodes apply the update and remain fully synchronized.


3. Perform an APPEND operation for the key "a" on the leader. Check the status of the different nodes. What changes have occurred and why (if any)?

Ans: 

After performing the APPEND operation on the leader, a new Raft log entry was created to store the appended value "mouse" for the key "a". This entry was then replicated to the two follower nodes. As a result, all three servers showed an increase in both commit_idx and last_applied from 4 to 5, confirming that the new entry was successfully committed and applied across the entire cluster.
The match_idx values on the leader also increased, indicating that both followers acknowledged the replication.
Additionally, because the APPEND operation creates a new log entry, the log_len value increases as well, reflecting the growth of the Raft log.
These changes occur because every write operation whether PUT or APPEND must be added to the leader’s log, replicated to a majority of the cluster, and then committed before it is applied to each node’s state machine. Once the entry is safely committed, all nodes update their state accordingly and remain fully synchronized.


4. Perform a GET operation for the key "a" on the leader. Check the status of the different nodes. What changes have occured and why (if any)?

Ans:

Performing the GET operation for the key “a” on the leader did not cause any changes in the Raft state across the nodes. The response correctly returned ["cat","dog","mouse"], showing that the previously committed PUT 
and APPEND operations were applied consistently. When checking the status of all three servers afterward, all Raft metrics such as log_len, commit_idx, and last_applied remained unchanged (commit_idx: 5, last_applied: 5). 
This is expected because a GET request is a read-only operation; it does not create a new log entry and therefore does not require replication or commitment through Raft. The leader simply serves the value already stored in its state machine, and the followers remain unaffected.



# Task 3

1. Shut down the server that acts as a leader. Report the status changes that you get from the servers that remain active after shutting down the leader. What is the new leader (if any)?

Ans:

After shutting down the original leader (node3), the two remaining servers, node1 and node2, automatically triggered a new leader election. In the new status output, node2 appears with "state": 2, indicating that it successfully became the new leader, while node1 shows "state": 0 and lists node2 as its leader.
The Raft term increased from term 1 to term 3, which is expected when a new election occurs following a leader failure. Both remaining servers also show increased commit_idx and last_applied values (now 6).
This happens because the new leader commits log entries that had already been replicated to a majority before the old leader crashed, ensuring the cluster continues with a consistent and up-to-date log.
In other words, the cluster remained synchronized despite the leader failure: the replicated but previously uncommitted entries were safely committed by the newly elected leader.


1. Perform a PUT operation for the key "a" on the new leader. Then, restart the previous leader, and indicate the changes in status for the three servers. Indicate the result of a GET operation for the key "a" to the previous leader.

Ans:

After performing the PUT operation on the new leader (node2), the key “a” was updated to the new value ["wolf", "bear"]. This write produced a new Raft log entry, which was replicated to the remaining follower. Both node1 and node2 show increased 
commit_idx and last_applied values of 7, indicating that the operation was successfully committed by a majority and applied to their state machines. After restarting the previous leader (node3), it rejoined the cluster as a follower and correctly recognized 
node2 as the current leader. A GET request to node3 returned the value ["wolf","bear"].


3. Has the PUT operation been replicated? Indicate which steps lead to a new election and which ones do not. Justify your answer using the statuses returned by the servers.

Ans:

Yes, the PUT operation was fully replicated. After restarting node3, its commit_idx and last_applied values immediately matched those of the other servers (both equal to 7), showing that it received and applied the missing log entries from the current leader. 
This confirms that the write was stored on a majority of servers before commitment, as required by Raft.

A new election occurred earlier because the original leader (node3) was shut down, leaving nodes 1 and 2 to hold an election. Since two nodes still formed a majority, node2 became the new leader. The PUT operation itself did not trigger a new election; it was processed normally because the cluster still had quorum. Only the leader shutdown caused a term increase and a new leader election.


4. Shut down two servers: first shut down a server that is not the leader, then shut down the leader. Report the status changes of the remaining server and explain what happened.

Ans:

After shutting down a follower (node1) and then shutting down the leader (node2), only node3 remained active in the cluster. The status output of node3 shows "has_quorum": False, meaning it no longer has a majority of servers available. Because Raft requires
a majority to elect a leader, node3 cannot promote itself to leader. This is reflected by "state": 0 (follower) and the stale "leader": TCPNode('node2:6001'), which refers to the now-offline leader. Since both partner nodes show status 0, node3 is isolated and unable 
to hold an election or commit new log entries. The server keeps its previous committed state (commit_idx: 7, last_applied: 7), but it cannot make progress or accept any writes.


5. Can you perform GET, PUT, or APPEND operations in this system state? Justify your answer.

Ans:

In this system state, GET operations may still work, but PUT and APPEND operations cannot be performed. Raft requires a majority of servers to be available in order to elect a leader and to replicate and commit any write operation. With only one node running, the system has no quorum, so no leader can be chosen. Without a leader, the cluster cannot accept any writes, since they must be logged, replicated, and committed through consensus. GET requests, however, do not modify the log and can still be answered using the remaining node’s local state. Therefore, reads may succeed, but writes are not possible until a majority of servers is restored.


6. Restart the servers and note down the changes in status. Describe what happened.

Ans:
After restarting all three servers, the cluster came back online and immediately stabilized. The nodes reconnected with each other, and Raft performed a fresh leader election. Node2 was selected as the new leader, while node1 and node3 rejoined as followers. 
Once the nodes discovered each other again, the system regained quorum, allowing the cluster to operate normally. Because the containers restart with a clean internal state, the term and log indices returned to their initial values, essentially putting the system into the 
same condition as a brand-new Raft cluster startup. Overall, the restart process restored a healthy cluster: one leader, two followers, and full communication between all nodes.


## Network Partition

For the first experiment, create a network partition with 2 servers (including the leader)
on the first partition and the 3 other servers on the other one. Indicate the changes that occur in the status of a server on the first partition and a server on the second partition. Reconnect the partitions and indicate what happens. What are the similarities and differences between the implementation of Raft used by your key/value service (based on the PySyncObj library) and the one shown in the Secret Lives of Data illustration from Task 1? How do you justify the differences?

Ans:

When the network was partitioned so that node1 and node2 were isolated from the remaining three servers, the two sides of the cluster showed very different behavior. On the side with only two servers, which also contained the previous leader (node1), the Raft status revealed that node1 could no longer communicate with a majority of the cluster. As a result, node1 repeatedly attempted to start a new election, but because it only saw node2, it was unable to gather the votes needed for leadership. Its status changed to “candidate,” showed no leader, and reported that it did not have quorum. In this partition, no leader could be elected and no new log entries could be committed. In contrast, the side of the network containing node3, node4, and node5 did have a majority. These three servers detected that the original leader was unreachable and triggered a new election. Because they formed a valid quorum, they successfully elected a new leader, which in the observed output was node5. The majority partition continued to function normally, accepted new log entries, and advanced its commit index, while the minority partition remained stuck without a functioning leader.
After the partitions were reconnected, the minority-side servers immediately received heartbeats and term information from the newly elected leader in the majority partition. Raft requires nodes to step down when they encounter a higher term, so node1 abandoned its futile election attempts and became a follower again. The previously disconnected nodes then synchronized their logs with the new leader, and the entire system returned to a consistent state with a single leader and uniform commit indices.

For the second experiment, create a network partition with 3 servers (including the
leader) on the first partition and the 2 other servers on the other one. Indicate the changes that occur in the status of a server on the first partition and a server on the second partition. Reconnect the partitions and indicate what happens. How does the implementation of Raft used by your key/value service (based on the PySyncObj library) compare to the one shown in the Secret Lives of Data illustration from Task 1?

Ans: 

In the second experiment, the network was split so that the leader (node4) stayed with node1 and node2 in the majority partition, while node3 and node5 ended up together in the minority. On the majority side, almost nothing changed: node4 remained the leader, all three nodes still had quorum, and their logs stayed in sync. The minority side, however, immediately lost access to the leader and couldn’t form a majority of their own. Node3 and node5 drifted into follower or candidate states, kept increasing their terms, and stayed behind in their logs because neither of them could win an election.
After the network was restored, everything quickly stabilized again. The majority side kept node4 as leader, and the minority nodes stepped down once they saw the leader’s term. They switched back to follower mode and would be brought up to date through log replication. Overall, this matches the Raft behavior shown in the Secret Lives of Data animation: the majority keeps functioning normally, while the minority stalls. The biggest difference is that PySyncObj tends to let isolated nodes increase their terms more aggressively, which is more of a practical implementation detail than a conceptual change.


# Task 4

1. Raft uses a leader election algorithm based on randomized timeouts and majority voting, but other leader election algorithms exist. One of them is the bully algorithm, which is described in Section 5.4.1 of the Distributed Systems book by van Steen and Tanenbaum. Imagine you update the PySyncObject library to use the bully algorithm for Raft (as described in the Distributed Systems book) instead of randomized timeouts and majority voting. What would happen in the first network partition from Task 3?

Ans: 

If the PySyncObj library used the bully algorithm instead of Raft’s randomized timeouts and majority voting, the behavior during the first network partition from Task 3 would be very different. In that experiment, the leader ended up in the smaller two-node partition. Under Raft, that leader becomes ineffective because it no longer has a majority and the larger partition elects a new legitimate leader. The bully algorithm, however, chooses the leader solely based on process IDs: the process with the highest ID among the reachable nodes always becomes the leader, regardless of how many nodes it can communicate with. This means that the node in the minority partition with the highest ID would continue to act as the leader, even though it does not have quorum. Meanwhile, the three nodes in the larger partition would elect their own leader, because they also see themselves as isolated from the "stronger" node. The result would be two leaders operating independently, a split-brain situation that violates the core safety guarantees normally provided by Raft. In short, using the bully algorithm in this context breaks Raft’s consensus model, because leadership becomes decoupled from majority availability.


2. Why is it that Raft cannot handle Byzantine failure? Explain in your own words.

Ans: 

Raft cannot tolerate Byzantine failures because it assumes that nodes may crash or disconnect, but they do not lie, forge messages, or behave arbitrarily. The correctness of Raft depends on the idea that all participating nodes follow the protocol honestly: leaders append the same log entries to all followers, followers respond truthfully, and all nodes relay consistent term and log information. In the presence of a Byzantine node, these assumptions break down completely—a malicious leader could send different log entries to different followers, followers could falsely report votes or terms, or nodes could impersonate each other. Raft has no mechanism to detect or correct such behavior, because it lacks cryptographic validation, multi-round agreement, or redundant message checking, all of which are required for Byzantine fault tolerance. As a result, a single Byzantine node can cause inconsistent logs, invalid commits, or even multiple leaders. Therefore, Raft is intentionally designed for environments with crash-failures only, and systems that require resilience against malicious or arbitrary faults must use Byzantine fault-tolerant algorithms instead.
