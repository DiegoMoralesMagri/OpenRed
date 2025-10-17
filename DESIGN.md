# openredNetwork - Design notes

This document records design ideas for a secure, fast node discovery and identity protocol for OpenRed.

Key goals
- Fast detection of newly joining nodes
- Strong, minimal cryptographic identity
- Ease of bootstrapping (can run on shared hosting or VPS)
- Auditability: every node announcement signed and verifiable

Core concepts
1. Identity
   - Each node has an Ed25519 keypair (signing key) used for persistent identity.
   - Node ID = base58(checksum(sha256(pubkey))) or multiformat-like cidv1 base32.
2. Transport and handshake
   - Use Noise XX pattern with X25519 ephemeral keys over TCP or QUIC for encrypted channels.
   - For minimal demo, use TCP with a Noise-like handshake implemented using libsodium.
3. Discovery
   - Combination of:
     a) Bootstrap static list (config)
     b) Gossip-based announcements (signed) using UDP multicast on local network for LAN
     c) DHT-based peerstore for global discovery (later)
4. Node announcement
   - Signed JSON blob: {id, pubkey, listen_addrs, timestamp, sequence, capabilities}
   - Signed with Ed25519; include signature and optionally a certificate chain.
5. Trust & reputation
   - Initially trust-by-web-of-trust: peers can vouch by signing other's announcement and broadcasting vouches.
   - Later add attestations and simple consensus for critical changes.

Security considerations
- Use non-malleable formats and avoid XML/HTML injection
- Replay protection via monotonic sequence + timestamp
- Rate-limit and validate all incoming announcements

Next steps
- Choose one discovery variant: LAN multicast + bootstrap list (fast/simple) OR DHT+gossip (robust/complex)
- Implement a minimal Python prototype that:
  * generates Ed25519 identity
  * announces on UDP multicast on local network
  * signs announcement
  * listens for announcements and verifies signatures


