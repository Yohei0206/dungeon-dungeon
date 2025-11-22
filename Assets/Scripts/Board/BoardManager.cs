using System.Collections.Generic;
using UnityEngine;
using UnityEngine.Tilemaps;

namespace Dungeon.Board
{
    public enum TileKind
    {
        Empty,
        Floor,
        Wall,
        Water,
        Decor
    }

    [System.Serializable]
    public struct TileDescriptor
    {
        public Vector3Int position;
        public TileBase tile;
        public TileKind kind;
        [Tooltip("True when this tile should block movement.")]
        public bool blocksMovement;
        [Tooltip("True when this tile should stop vision propagation.")]
        public bool blocksVision;
        [Tooltip("Marks the tile as shadowed or darkened (used for FoW penalties).")]
        public bool isShadow;
    }

    /// <summary>
    /// Provides lookup access to the terrain, shadow and fog tilemaps and the logical tile descriptors
    /// so other systems can query what lives at a grid coordinate.
    /// </summary>
    public class BoardManager : MonoBehaviour
    {
        [Header("Tilemaps")]
        [SerializeField] private Grid grid;
        [SerializeField] private Tilemap terrainTilemap;
        [SerializeField] private Tilemap shadowTilemap;
        [SerializeField] private Tilemap fogTilemap;

        [Header("Tile Descriptors")]
        [SerializeField] private List<TileDescriptor> tiles = new();

        private readonly Dictionary<Vector3Int, TileDescriptor> lookup = new();

        public Grid Grid => grid;
        public Tilemap TerrainTilemap => terrainTilemap;
        public Tilemap ShadowTilemap => shadowTilemap;
        public Tilemap FogTilemap => fogTilemap;

        private void Awake()
        {
            BuildLookup();
        }

        private void OnValidate()
        {
            BuildLookup();
        }

        private void BuildLookup()
        {
            lookup.Clear();
            foreach (var descriptor in tiles)
            {
                lookup[descriptor.position] = descriptor;
            }
        }

        public bool TryGetTile(Vector3Int gridPosition, out TileDescriptor descriptor)
        {
            return lookup.TryGetValue(gridPosition, out descriptor);
        }

        public TileKind GetTileKind(Vector3Int gridPosition)
        {
            return lookup.TryGetValue(gridPosition, out var descriptor) ? descriptor.kind : TileKind.Empty;
        }

        public bool IsBlockingVision(Vector3Int gridPosition)
        {
            return lookup.TryGetValue(gridPosition, out var descriptor) && descriptor.blocksVision;
        }

        public bool IsShadow(Vector3Int gridPosition)
        {
            return lookup.TryGetValue(gridPosition, out var descriptor) && descriptor.isShadow;
        }

        public IEnumerable<Vector3Int> GetAllPositions()
        {
            return lookup.Keys;
        }

        public void PaintFog(IEnumerable<Vector3Int> positions, TileBase fogTile)
        {
            if (fogTilemap == null)
            {
                return;
            }

            foreach (var position in positions)
            {
                fogTilemap.SetTile(position, fogTile);
            }
        }

        public void ClearFog(IEnumerable<Vector3Int> positions)
        {
            if (fogTilemap == null)
            {
                return;
            }

            foreach (var position in positions)
            {
                fogTilemap.SetTile(position, null);
            }
        }
    }
}
