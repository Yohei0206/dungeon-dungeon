using System;
using System.Linq;
using UnityEngine;

namespace Dungeon.Stats
{
    [Serializable]
    public class CharacterStats
    {
        [SerializeField] private JobDefinition job;
        [SerializeField, Min(1)] private int level = 1;

        [SerializeField] private int maxHp;
        [SerializeField] private int attack;
        [SerializeField] private int defense;
        [SerializeField] private int luck;
        [SerializeField] private int vision;
        [SerializeField] private int move;

        public JobDefinition Job => job;
        public int Level => level;
        public int MaxHp => maxHp;
        public int Attack => attack;
        public int Defense => defense;
        public int Luck => luck;
        public int Vision => vision;
        public int Move => move;

        public CharacterStats(JobDefinition jobDefinition)
        {
            job = jobDefinition;
            level = 1;
            ApplyInitialStats();
        }

        public void ApplyInitialStats()
        {
            if (job == null)
            {
                Debug.LogWarning("CharacterStats was created without a JobDefinition.");
                return;
            }

            var initial = job.InitialStats;
            maxHp = initial.hp;
            attack = initial.attack;
            defense = initial.defense;
            luck = initial.luck;
            vision = initial.vision;
            move = initial.move;
        }

        public void LevelUp()
        {
            if (job == null)
            {
                Debug.LogWarning("Cannot level up without a JobDefinition.");
                return;
            }

            level += 1;
            ApplyGrowth(job.GrowthRates);
            ApplyTraitHooksAfterLevelUp();
        }

        private void ApplyGrowth(StatGrowthRates growth)
        {
            maxHp += Mathf.RoundToInt(growth.hp);
            attack += Mathf.RoundToInt(growth.attack);
            defense += Mathf.RoundToInt(growth.defense);
            luck += Mathf.RoundToInt(growth.luck);
            vision += Mathf.RoundToInt(growth.vision);
            move += Mathf.RoundToInt(growth.move);
        }

        public int ResolveBossVictoryPoints(int baseVictoryPoints)
        {
            if (job == null)
            {
                return baseVictoryPoints;
            }

            float bonus = job.GetTraitMagnitude(JobTraitType.BossVictoryBonus);
            return Mathf.RoundToInt(baseVictoryPoints * (1f + bonus));
        }

        public bool TryAvoidTrap(float trapDifficulty)
        {
            float baseChance = Mathf.Clamp01((luck + 1f) / Math.Max(1f, trapDifficulty));
            float traitBonus = job?.GetTraitMagnitude(JobTraitType.TrapEvasion) ?? 0f;
            float finalChance = Mathf.Clamp01(baseChance + traitBonus);
            return UnityEngine.Random.value <= finalChance;
        }

        public int ApplyVisionBonus(int currentVision)
        {
            float bonus = job?.GetTraitMagnitude(JobTraitType.BonusVision) ?? 0f;
            return currentVision + Mathf.RoundToInt(bonus);
        }

        public int ApplyMovementBonus(int currentMove)
        {
            float bonus = job?.GetTraitMagnitude(JobTraitType.BonusMovement) ?? 0f;
            return currentMove + Mathf.RoundToInt(bonus);
        }

        private void ApplyTraitHooksAfterLevelUp()
        {
            if (job == null)
            {
                return;
            }

            var visionBonus = job.Traits.FirstOrDefault(t => t.Type == JobTraitType.BonusVision);
            if (visionBonus != null)
            {
                vision += Mathf.RoundToInt(visionBonus.Magnitude);
            }

            var movementBonus = job.Traits.FirstOrDefault(t => t.Type == JobTraitType.BonusMovement);
            if (movementBonus != null)
            {
                move += Mathf.RoundToInt(movementBonus.Magnitude);
            }
        }
    }
}
