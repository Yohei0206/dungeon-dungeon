using System.Collections.Generic;
using UnityEngine;
using UnityEngine.Tilemaps;

namespace Dungeon.Board
{
    /// <summary>
    /// Computes player vision and keeps the fog-of-war tilemap updated based on profession-specific rules.
    /// </summary>
    public class FogOfWarController : MonoBehaviour
    {
        [SerializeField] private BoardManager boardManager;
        [SerializeField] private TileBase fogTile;

        [Header("Vision Profiles")]
        [SerializeField] private VisionProfile rogueProfile;
        [SerializeField] private VisionProfile hunterProfile;
        [SerializeField] private VisionProfile defaultProfile;

        private readonly HashSet<Vector3Int> buffer = new();
        private readonly List<Vector3Int> toReveal = new();
        private readonly List<Vector3Int> toHide = new();

        public void UpdateFog(Vector3Int origin, Profession profession)
        {
            if (boardManager == null)
            {
                Debug.LogWarning("FogOfWarController requires a BoardManager reference.");
                return;
            }

            var profile = ResolveProfile(profession);
            buffer.Clear();
            toReveal.Clear();
            toHide.Clear();

            RunFieldOfView(origin, profile);

            foreach (var position in boardManager.GetAllPositions())
            {
                if (buffer.Contains(position))
                {
                    toReveal.Add(position);
                }
                else
                {
                    toHide.Add(position);
                }
            }

            boardManager.ClearFog(toReveal);
            boardManager.PaintFog(toHide, fogTile);
        }

        private VisionProfile ResolveProfile(Profession profession)
        {
            return profession switch
            {
                Profession.Rogue when rogueProfile != null => rogueProfile,
                Profession.Hunter when hunterProfile != null => hunterProfile,
                _ when defaultProfile != null => defaultProfile,
                _ => VisionProfile.CreateRuntimeProfile(profession, 6, 1, false)
            };
        }

        private void RunFieldOfView(Vector3Int origin, VisionProfile profile)
        {
            var queue = new Queue<(Vector3Int position, int cost, bool peeked)>();
            queue.Enqueue((origin, 0, false));
            buffer.Add(origin);

            while (queue.Count > 0)
            {
                var current = queue.Dequeue();
                if (current.cost >= profile.BaseRange)
                {
                    continue;
                }

                foreach (var direction in CardinalDirections())
                {
                    var next = current.position + direction;
                    var cost = current.cost + 1;

                    if (boardManager.TryGetTile(next, out var descriptor))
                    {
                        var effectiveRange = profile.BaseRange - (descriptor.isShadow ? profile.ShadowPenalty : 0);
                        if (cost > effectiveRange)
                        {
                            continue;
                        }

                        if (buffer.Add(next))
                        {
                            var blocked = descriptor.blocksVision;

                            if (!blocked)
                            {
                                queue.Enqueue((next, cost, current.peeked));
                            }
                            else if (!current.peeked && profile.PeekBeyondBlocker && cost < effectiveRange)
                            {
                                queue.Enqueue((next, cost + 1, true));
                            }
                        }
                    }
                }
            }
        }

        private static IEnumerable<Vector3Int> CardinalDirections()
        {
            yield return Vector3Int.up;
            yield return Vector3Int.down;
            yield return Vector3Int.left;
            yield return Vector3Int.right;
        }
    }
}
