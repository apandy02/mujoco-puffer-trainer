from gymnasium.envs.registration import register


register(
    id="Ant-v5",
    entry_point="updated_envs.ant_v5:AntEnv",
    max_episode_steps=1000,
    reward_threshold=6000.0,
)
