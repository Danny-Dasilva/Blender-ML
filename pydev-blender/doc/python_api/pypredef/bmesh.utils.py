'''BMesh Utilities (bmesh.utils)
   This module provides access to blenders bmesh data structures.
   
'''


def edge_rotate(edge, ccw=False):
   '''Rotate the edge and return the newly created edge.
      If rotating the edge fails, None will be returned.
      
      Arguments:
      @edge (bmesh.types.BMEdge): The edge to rotate.
      @ccw (boolean): When True the edge will be rotated counter clockwise.

      @returns (bmesh.types.BMEdge): The newly rotated edge.
   '''

   return bmesh.types.BMEdge

def edge_split(edge, vert, fac):
   '''Split an edge, return the newly created data.
      
      Arguments:
      @edge (bmesh.types.BMEdge): The edge to split.
      @vert (bmesh.types.BMVert): One of the verts on the edge, defines the split direction.
      @fac (float): The point on the edge where the new vert will be created [0 - 1].

      @returns (tuple): The newly created (edge, vert) pair.
   '''

   return tuple

def face_flip(faces):
   '''Flip the faces direction.
      
      Arguments:
      @face (bmesh.types.BMFace): Face to flip.

   '''

   pass

def face_join(faces, remove=True):
   '''Joins a sequence of faces.
      
      Arguments:
      @faces (bmesh.types.BMFace): Sequence of faces.
      @remove (boolean): Remove the edges and vertices between the faces.

      @returns (bmesh.types.BMFace): The newly created face or None on failure.
   '''

   return bmesh.types.BMFace

def face_split(face, vert_a, vert_b, coords=(), use_exist=True, example=None):
   '''Face split with optional intermediate points.
      
      Arguments:
      @face (bmesh.types.BMFace): The face to cut.
      @vert_a (bmesh.types.BMVert): First vertex to cut in the face (face must contain the vert).
      @vert_b (bmesh.types.BMVert): Second vertex to cut in the face (face must contain the vert).
      @coords (sequence of float triplets): Optional argument to define points inbetween *vert_a* and *vert_b*.
      @use_exist (boolean): .Use an existing edge if it exists (Only used when *coords* argument is empty or omitted)
      @example (bmesh.types.BMEdge): Newly created edge will copy settings from this one.

      @returns ((bmesh.types.BMFace, bmesh.types.BMLoop) pair): The newly created face or None on failure.
   '''

   return (bmesh.types.BMFace, bmesh.types.BMLoop) pair

def face_split_edgenet(face, edgenet):
   '''Splits a face into any number of regions defined by an edgenet.
      
      Arguments:
      @face (bmesh.types.BMFace): The face to split.
      @edgenet (bmesh.types.BMEdge): Sequence of edges.

      @returns (tuple of (bmesh.types.BMFace)): The newly created faces.
   '''

   return tuple of (bmesh.types.BMFace)

def face_vert_separate(face, vert):
   '''Rip a vertex in a face away and add a new vertex.
      
      Arguments:
      @face (bmesh.types.BMFace): The face to separate.
      @vert (bmesh.types.BMVert): A vertex in the face to separate.:return vert: The newly created vertex or None on failure.
      :rtype vert: bmesh.types.BMVert
      .. note::
      This is the same as loop_separate, and has only been added for convenience.
      

   '''

   pass

def loop_separate(loop):
   '''Rip a vertex in a face away and add a new vertex.
      
      Arguments:
      @loop (bmesh.types.BMLoop): The loop to separate.:return vert: The newly created vertex or None on failure.
      :rtype vert: bmesh.types.BMVert
      

   '''

   pass

def vert_collapse_edge(vert, edge):
   '''Collapse a vertex into an edge.
      
      Arguments:
      @vert (bmesh.types.BMVert): The vert that will be collapsed.
      @edge (bmesh.types.BMEdge): The edge to collapse into.

      @returns (bmesh.types.BMEdge): The resulting edge from the collapse operation.
   '''

   return bmesh.types.BMEdge

def vert_collapse_faces(vert, edge, fac, join_faces):
   '''Collapses a vertex that has only two manifold edges onto a vertex it shares an edge with.
      
      Arguments:
      @vert (bmesh.types.BMVert): The vert that will be collapsed.
      @edge (bmesh.types.BMEdge): The edge to collapse into.
      @fac (float): The factor to use when merging customdata [0 - 1].

      @returns (bmesh.types.BMEdge): The resulting edge from the collapse operation.
   '''

   return bmesh.types.BMEdge

def vert_dissolve(vert):
   '''Dissolve this vertex (will be removed).
      
      Arguments:
      @vert (bmesh.types.BMVert): The vert to be dissolved.

      @returns (bool): True when the vertex dissolve is successful.
   '''

   return bool

def vert_separate(vert, edges):
   '''Separate this vertex at every edge.
      
      Arguments:
      @vert (bmesh.types.BMVert): The vert to be separated.
      @edges (bmesh.types.BMEdge): The edges to separated.

      @returns (tuple of bmesh.types.BMVert): The newly separated verts (including the vertex passed).
   '''

   return tuple of bmesh.types.BMVert

def vert_splice(vert, vert_target):
   '''Splice vert into vert_target.
      
      Arguments:
      @vert (bmesh.types.BMVert): The vertex to be removed.
      @vert_target (bmesh.types.BMVert): The vertex to use.

      Note: The verts mustn't share an edge or face.
   '''

   pass

