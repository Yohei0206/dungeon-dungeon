using System;
using System.Collections.Generic;
using System.Linq;
using UnityEngine;

namespace Dungeon.Stats
{
    public enum JobTraitType
    {
        None = 0,
        BossVictoryBonus = 1,
        TrapEvasion = 2,
        BonusVision = 3,
        BonusMovement = 4,
    }

    [Serializable]
    public class JobTrait
    {
        [SerializeField] private JobTraitType type = JobTraitType.None;
        [SerializeField, Range(0f, 5f)] private float magnitude = 0f;
        [SerializeField, TextArea] private string description = string.Empty;

        public JobTraitType Type => type;
        public float Magnitude => magnitude;
        public string Description => description;
    }

    [Serializable]
    public struct StatBlock
    {
        public int hp;
        public int attack;
        public int defense;
        public int luck;
        public int vision;
        public int move;

        public static StatBlock Default()
        {
            return new StatBlock
            {
                hp = 10,
                attack = 2,
                defense = 1,
                luck = 0,
                vision = 4,
                move = 4,
            };
        }
    }

    [Serializable]
    public struct StatGrowthRates
    {
        public float hp;
        public float attack;
        public float defense;
        public float luck;
        public float vision;
        public float move;

        public static StatGrowthRates Default()
        {
            return new StatGrowthRates
            {
                hp = 1.5f,
                attack = 0.75f,
                defense = 0.5f,
                luck = 0.25f,
                vision = 0.1f,
                move = 0.05f,
            };
        }
    }

    [CreateAssetMenu(fileName = "JobDefinition", menuName = "Dungeon/Job Definition")]
    public class JobDefinition : ScriptableObject
    {
        [Header("Display")]
        [SerializeField] private string jobName = "New Job";

        [Header("Stats")]
        [SerializeField] private StatBlock initialStats = StatBlock.Default();
        [SerializeField] private StatGrowthRates growthRates = StatGrowthRates.Default();

        [Header("Traits")]
        [SerializeField] private List<JobTrait> traits = new();

        public string JobName => jobName;
        public StatBlock InitialStats => initialStats;
        public StatGrowthRates GrowthRates => growthRates;
        public IReadOnlyList<JobTrait> Traits => traits;

        public float GetTraitMagnitude(JobTraitType type)
        {
            return traits.FirstOrDefault(t => t.Type == type)?.Magnitude ?? 0f;
        }
    }
}
