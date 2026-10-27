# Memory-bar cancellation: native event boundary

Run https://github.com/Harsh23Kashyap/Chatify/actions/runs/40465087933 shard0 failed 39/40 on the runtime quiet cancellation check, not estimate widths. The unchanged case also fails locally.

The exact-check diagnostic reproduced the mechanism: at its original 10ms check, matchMedia.matches is true but no native change event has fired. Three original animations are still paused at49.974ms. 2.4ms later the browser delivers the change event and all three original animations are idle/currentTime=null. They did not finish naturally because they were paused. Source attaches cancellation to that native event.

The test now records original animation references, subscribes before media emulation, waits for delivery using the existing bounded waitForFunction default, and checks the exact states captured synchronously at that event. It requires all three original paused animations retired (idle/currentTime=null), and keeps the existing zero-animation, geometry, duration/easing, four motion levels and two-width assertions. No product change, timing increase, retry, or exception waiver. Two full local16-combination runs pass; the second uses the final bounded event marker implementation.
