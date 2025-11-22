using UnityEngine;

namespace Dungeon.Board
{
    [CreateAssetMenu(fileName = "VisionProfile", menuName = "Dungeon/Vision Profile", order = 0)]
    public class VisionProfile : ScriptableObject
    {
        [SerializeField] private Profession profession = Profession.Rogue;
        [SerializeField, Min(1)] private int baseRange = 6;
        [SerializeField, Min(0)] private int shadowPenalty = 1;
        [SerializeField] private bool peekBeyondBlocker = false;

        public Profession Profession => profession;
        public int BaseRange => baseRange;
        public int ShadowPenalty => shadowPenalty;
        public bool PeekBeyondBlocker => peekBeyondBlocker;

        public static VisionProfile CreateRuntimeProfile(Profession profession, int baseRange, int shadowPenalty, bool peekBeyondBlocker)
        {
            var profile = CreateInstance<VisionProfile>();
            profile.profession = profession;
            profile.baseRange = baseRange;
            profile.shadowPenalty = shadowPenalty;
            profile.peekBeyondBlocker = peekBeyondBlocker;
            return profile;
        }
    }

    public enum Profession
    {
        Rogue,
        Hunter,
        Warrior,
        Mage
    }
}
