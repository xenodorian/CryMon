#!/usr/bin/env node
import { registerAgent, claimFile, releaseFile, sendMessage, recordDecision } from './server.js';

const [cmd, ...args] = process.argv.slice(2);

switch (cmd) {
  case 'register':
    registerAgent(args[0], args.slice(1));
    break;
  case 'claim':
    console.log(claimFile(args[0], args[1], args.slice(2).join(' ')));
    break;
  case 'release':
    releaseFile(args[0], args[1]);
    break;
  case 'message':
    sendMessage(args[0], args[1], args.slice(2).join(' '));
    break;
  case 'decision':
    recordDecision(args[0], args[1], args[2]);
    break;
  default:
    console.log('Commands: register claim release message decision');
}
