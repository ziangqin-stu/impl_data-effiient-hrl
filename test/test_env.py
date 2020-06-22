"""Test Ant Enviornments"""
import sys
import os
from utils import get_env

import torch
sys.path.append(os.path.abspath(os.path.dirname(os.getcwd())))

import numpy as np
import wandb
from utils import envnames_ant, log_video_hrl, ParamDict
from network import ActorLow, ActorHigh
wandb.init(project="ziang-hiro")
import gym
from pyvirtualdisplay import Display
from environments.create_maze_env import create_maze_env


def show_env_property(env_name):
    env = create_maze_env.create_maze_env(env_name=env_name)
    print("\n\n-------------------------------------------------------------------------------------------------------")
    print(
        "{}: \n    MAZE_HEIGHT: {}\n    MAZE_SIZE_SCALING:{}\n    MAZE_STRUCTURE: {}".format(env_name, env.MAZE_HEIGHT,
                                                                                             env.MAZE_SIZE_SCALING,
                                                                                             env.MAZE_STRUCTURE))
    print("    MODEL_CLASS: {}".format(env.MODEL_CLASS))
    print(
        "    action_space: \n        dtype: {}\n        high: {}\n        low: {}\n        shape: {}\n        np_random: {}".format(
            env.action_space.dtype, env.action_space.high, env.action_space.low, env.action_space.shape,
            env.action_space.np_random))
    print(
        "    observation_space: \n        dtype: {}\n        high: {}\n        low: {}\n        shape: {}\n        np_random: {}".format(
            env.observation_space.dtype, env.observation_space.high[:14], env.observation_space.low[:14],
            env.observation_space.shape, env.observation_space.np_random))
    print("    reward_range: {}".format(env.reward_range))
    print("    movable_blocks: {}".format(env.movable_blocks))
    print("    wrapped_env: {}".format(env.wrapped_env))
    print("-------------------------------------------------------------------------------------------------------")
    return env


def show_envs():
    for env_name in envnames_ant:
        show_env_property(env_name)


def interact_env(env_name, video=False):
    env = create_maze_env(env_name=env_name)
    print('\n    > Collecting random trajectory...')
    done = False
    step = 1
    obs = env.reset()
    frame_buffer = []
    while not (done or step > 100):
        if video:
            frame_buffer.append(env.render(mode='rgb_array'))
        action = env.action_space.sample()
        obs, reward, done, info = env.step(action)
        step += 1
        print(f"      > Reward: {reward:.3f}")
    print('    > Finished collection', end='')
    if video:
        frame_buffer = np.array(frame_buffer).transpose(0, 3, 1, 2)
        wandb.log({"video": wandb.Video(frame_buffer, fps=30, format="mp4")})
        print(', saved video.\n')
        env.close()
    else:
        print('.\n')
    return env


def interact_envs_display(video=False):
    if video:
        display = Display(backend='xvfb')
        display.start()
    for env_name in envnames_ant:
        interact_env(env_name, video=video)
    if video:
        display.popen.kill()


def test_env(env_name):
    env = get_env(env_name)
    print(env.spec.id)


def test_log_video_hrl(use_cuda=False):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu") if use_cuda else "cpu"
    policy_params = ParamDict(
        c=10,
    )
    params = ParamDict(
        policy_params=policy_params,
        use_cuda=False
    )
    for env_name in envnames_ant:
        env = create_maze_env(env_name=env_name)
        state_dim = env.observation_space.shape[0]
        action_dim = env.action_space.shape[0]
        max_action = float(env.action_space.high[0])
        actor_low = ActorLow(state_dim, action_dim, max_action).to(device)
        actor_high = ActorHigh(state_dim, max_action).to(device)
        log_video_hrl(env_name, actor_low, actor_high, params)


if __name__ == "__main__":
    gym.logger.set_level(40)
    # show_envs()
    # interact_envs_display(video=True)
    # interact_env('AntMaze', video=False)
    # test_env("InvertedPendulum-v2")
    test_log_video_hrl()
