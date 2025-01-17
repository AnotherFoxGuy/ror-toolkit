#ifndef __FlexObj_H__
#define __FlexObj_H__

//body

#include "Ogre.h"
//#include "Beam.h"

using namespace Ogre;


//class Beam;

class FlexObj
{
private:
typedef struct
{
	Vector3 vertex;
	Vector3 normal;
//	Vector3 color;
	Vector2 texcoord;
} CoVertice_t;

typedef struct
{
	Vector3 vertex;
} posVertice_t;

typedef struct
{
	Vector3 normal;
//	Vector3 color;
	Vector2 texcoord;
} norVertice_t;

	Ogre::MeshPtr msh;
	SubMesh** subs;
	VertexDeclaration* decl;
	HardwareVertexBufferSharedPtr vbuf;

	size_t nVertices;
	size_t vbufCount;
	//shadow
	union
	{
	float *shadowposvertices;
	posVertice_t *coshadowposvertices;
	};
	union
	{
	float *shadownorvertices;
	norVertice_t *coshadownorvertices;
	};

	union
	{
	float *vertices;
	CoVertice_t *covertices;
	};
	//nodes
	int *nodeIDs;

	size_t ibufCount;
	unsigned short *faces;
	node_t *nodes;
	int nbrays;
	SceneManager *smanager;

	float *sref;

public:


	FlexObj(SceneManager *manager, node_t *nds, int numtexcoords, Vector3* texcoords, int numtriangles, int* triangles, int numsubmeshes, int* subtexindex, int* subtriindex, char* texname, char* name, int* subisback, char* backtexname, char* transtexname)
    {
		unsigned int i;
		int j;
		/*
		//okay, we munch a bit the data to optimize submesh count
		Vector3* texcoords=(Vector3*)malloc(sizeof(Vector3)*numtexcoords);
		int* triangles=(int*)malloc(sizeof(int)*3*numtriangles);
		int numsubmeshes=3;
		int subtexindex[4];
		int subtriindex[4];
		int subisback[3]={0,1,2};
		int numtex[3]={0,0,0};
		int numtri[3]={0,0,0};
		int postex[3]={0,0,0};
		int postri[3]={0,0,0};
		for (j=0; j<onumsubmeshes; j++)
		{
			int type=0;
			if (j<numsubmeshes-1)
			{
				type=osubisback[j+1];
			}
			numtex[type]+=osubtexindex[j+1]-osubtexindex[j];
			numtri[type]+=osubtriindex[j+1]-osubtriindex[j];
		}
		postex[0]=0; postex[1]=numtex[0]; postex[2]=numtex[0]+numtex[1];
		subtexindex[0]=0; subtexindex[1]=numtex[0]; subtexindex[2]=numtex[0]+numtex[1]; subtexindex[3]=numtex[0]+numtex[1]+numtex[2];
		postri[0]=0; postri[1]=numtri[0]; postri[2]=numtri[0]+numtri[1];
		subtriindex[0]=0; subtriindex[1]=numtri[0]; subtriindex[2]=numtri[0]+numtri[1]; subtriindex[3]=numtri[0]+numtri[1]+numtri[2];
		for (j=0; j<onumsubmeshes; j++)
		{
			int type=0;
			if (j<numsubmeshes-1)
			{
				type=osubisback[j+1];
			}
			for (i=0; i<osubtexindex[j+1]-osubtexindex[j]; i++)
			{
				texcoords[postex[type]]=otexcoords[osubtexindex[j]+i];
			}
			postex[type]+=osubtexindex[j+1]-osubtexindex[j];
			for (i=0; i<osubtriindex[j+1]-osubtriindex[j]; i++)
			{
				int k;
				for (k=0; k<3; k++)
					triangles[postri[type]*3+k]=otriangles[(osubtriindex[j]+i)*3+k];
			}
			postri[type]+=osubtriindex[j+1]-osubtriindex[j];
		}
*/
		//finished munching
		smanager=manager;
		nodes=nds;
		/// Create the mesh via the MeshManager
        msh = MeshManager::getSingleton().createManual(name, "General");

        /// Create submeshes
		subs=(SubMesh**)malloc(numsubmeshes*sizeof(SubMesh*));
		for (j=0; j<numsubmeshes; j++)
		{
			subs[j] = msh->createSubMesh();
			//materials
			if (j<numsubmeshes-1)
			{
				if (subisback[j+1]==0) subs[j]->setMaterialName(texname);
				if (subisback[j+1]==1) subs[j]->setMaterialName(backtexname);
				if (subisback[j+1]==2) subs[j]->setMaterialName(transtexname);
			}
			else
				subs[j]->setMaterialName(texname);
		};

        /// Define the vertices (8 vertices, each consisting of 3 groups of 3 floats
        nVertices = numtexcoords;
        vbufCount = (2*3+2)*nVertices;
		vertices=(float*)malloc(vbufCount*sizeof(float));
		//shadow
		shadownorvertices=(float*)malloc(nVertices*(3+2)*sizeof(float));
		shadowposvertices=(float*)malloc(nVertices*3*2*sizeof(float));
		nodeIDs=(int*)malloc(nVertices*sizeof(int));

		//define node ids
		for (i=0; i<nVertices; i++)
		{
			nodeIDs[i]=(int)(texcoords[i].x);
		}

		//textures coordinates
		for (i=0; i<nVertices; i++)
		{
			covertices[i].texcoord=Vector2(texcoords[i].y,texcoords[i].z);
		}

        /// Define triangles
        /// The values in this table refer to vertices in the above table
        ibufCount = 3*numtriangles;
        faces=(unsigned short*)malloc(ibufCount*sizeof(unsigned short));
		for (i=0; i<ibufCount; i++)
		{
			faces[i]=findID(i/3, triangles[i], numsubmeshes, subtexindex, subtriindex);
		}

		sref=(float*)malloc(numtriangles*sizeof(float));

		for (i=0; i<(unsigned int)numtriangles;i++)
		{
			Vector3 v1, v2;
			v1=nodes[nodeIDs[faces[i*3+1]]].Position-nodes[nodeIDs[faces[i*3]]].Position;
			v2=nodes[nodeIDs[faces[i*3+2]]].Position-nodes[nodeIDs[faces[i*3]]].Position;
			v1=v1.crossProduct(v2);
			sref[i]=v1.length()*2.0;
		}


		//update coords
		updateVertices();



        /// Create vertex data structure for vertices shared between submeshes
        msh->sharedVertexData = new VertexData();
        msh->sharedVertexData->vertexCount = nVertices;


        /// Create declaration (memory format) of vertex data
        decl = msh->sharedVertexData->vertexDeclaration;
        size_t offset = 0;
        decl->addElement(0, offset, VET_FLOAT3, VES_POSITION);
        offset += VertexElement::getTypeSize(VET_FLOAT3);
        decl->addElement(0, offset, VET_FLOAT3, VES_NORMAL);
        offset += VertexElement::getTypeSize(VET_FLOAT3);
//        decl->addElement(0, offset, VET_FLOAT3, VES_DIFFUSE);
//        offset += VertexElement::getTypeSize(VET_FLOAT3);
        decl->addElement(0, offset, VET_FLOAT2, VES_TEXTURE_COORDINATES, 0);
        offset += VertexElement::getTypeSize(VET_FLOAT2);


        /// Allocate vertex buffer of the requested number of vertices (vertexCount) 
        /// and bytes per vertex (offset)
        vbuf = 
          HardwareBufferManager::getSingleton().createVertexBuffer(
              offset, msh->sharedVertexData->vertexCount, HardwareBuffer::HBU_DYNAMIC_WRITE_ONLY_DISCARDABLE);

        /// Upload the vertex data to the card
        vbuf->writeData(0, vbuf->getSizeInBytes(), vertices, true);


        /// Set vertex buffer binding so buffer 0 is bound to our vertex buffer
        VertexBufferBinding* bind = msh->sharedVertexData->vertexBufferBinding; 
        bind->setBinding(0, vbuf);




        /// Set parameters of the submeshes
		for (j=0; j<numsubmeshes; j++)
		{
			int smcount=3*(subtriindex[j+1]-subtriindex[j]);
	        subs[j]->useSharedVertices = true;
			/// Allocate index buffer of the requested number of vertices (ibufCount) 
			HardwareIndexBufferSharedPtr ibuf = HardwareBufferManager::getSingleton().
			 createIndexBuffer(
				 HardwareIndexBuffer::IT_16BIT, 
					smcount, 
					HardwareBuffer::HBU_STATIC_WRITE_ONLY);

			/// Upload the index data to the card
			ibuf->writeData(0, ibuf->getSizeInBytes(), &faces[subtriindex[j]*3], true);
		    subs[j]->indexData->indexBuffer = ibuf;
			subs[j]->indexData->indexCount = smcount;
	        subs[j]->indexData->indexStart = 0;
		}


        /// Set bounding information (for culling)
        msh->_setBounds(AxisAlignedBox(-100,-100,-100,100,100,100));
        msh->_setBoundingSphereRadius(100);


        /// Notify Mesh object that it has been loaded
        msh->load();
		msh->buildEdgeList();

    }

//find the zeroed id of the node v in the context of the tidx triangle
int findID(int tidx, int v, int numsubmeshes, int* subtexindex, int* subtriindex)
{
	int j;
	//first: find the context from the triangle index tidx
	int context;
	for (context=0; context<numsubmeshes+1; context++) if (tidx<subtriindex[context]) {context--;break;};
	//okay, now search in the vertice block corresponding to the context
	for (j=subtexindex[context]; j<subtexindex[context+1]; j++) if (nodeIDs[j]==v) return j;
	return 0;
}

/*Vector3 updateVertices()
{
	unsigned int i;
	Vector3 center;
	center=(nodes[nodeIDs[0]].Position+nodes[nodeIDs[1]].Position)/2.0;
	for (i=0; i<nVertices; i++)
	{
		covertices[i].vertex=nodes[nodeIDs[i]].Position-center;
		//normals
		covertices[i].normal=covertices[i].vertex;
		covertices[i].normal.normalise();
	}

	return center;
}
*/

//with normals
Vector3 updateVertices()
{
	unsigned int i;
	Vector3 center;
	center=(nodes[nodeIDs[0]].Position+nodes[nodeIDs[1]].Position)/2.0;
	for (i=0; i<nVertices; i++)
	{
		//set position
		covertices[i].vertex=nodes[nodeIDs[i]].Position-center;
		//reset normals
		covertices[i].normal=Vector3::ZERO;
	}
	//accumulate normals per triangle
	for (i=0; i<ibufCount/3; i++)
	{
		Vector3 v1, v2;
		v1=nodes[nodeIDs[faces[i*3+1]]].Position-nodes[nodeIDs[faces[i*3]]].Position;
		v2=nodes[nodeIDs[faces[i*3+2]]].Position-nodes[nodeIDs[faces[i*3]]].Position;
		v1=v1.crossProduct(v2);
		float s=v1.length();
		//avoid large tris
		if (s>sref[i]) 
		{
			covertices[faces[i*3+1]].vertex=covertices[faces[i*3]].vertex+Vector3(0.1,0,0);
			covertices[faces[i*3+2]].vertex=covertices[faces[i*3]].vertex+Vector3(0,0,0.1);
		}
		//v1.normalise();
		v1=v1/s;
		covertices[faces[i*3]].normal+=v1;
		covertices[faces[i*3+1]].normal+=v1;
		covertices[faces[i*3+2]].normal+=v1;
	}
	//normalize
	for (i=0; i<nVertices; i++)
	{
		covertices[i].normal.normalise();
	}

	return center;
}

//with normals
Vector3 updateShadowVertices()
{
	unsigned int i;
	Vector3 center;
	center=(nodes[nodeIDs[0]].Position+nodes[nodeIDs[1]].Position)/2.0;
	for (i=0; i<nVertices; i++)
	{
		//set position
		coshadowposvertices[i].vertex=nodes[nodeIDs[i]].Position-center;
		coshadowposvertices[i+nVertices].vertex=nodes[nodeIDs[i]].Position-center;
		//reset normals
		coshadownorvertices[i].normal=Vector3::ZERO;
	}
	//accumulate normals per triangle
	for (i=0; i<ibufCount/3; i++)
	{
		Vector3 v1, v2;
		v1=nodes[nodeIDs[faces[i*3+1]]].Position-nodes[nodeIDs[faces[i*3]]].Position;
		v2=nodes[nodeIDs[faces[i*3+2]]].Position-nodes[nodeIDs[faces[i*3]]].Position;
		v1=v1.crossProduct(v2);
		float s=v1.length();
		//avoid large tris
		if (s>sref[i]) 
		{
			coshadowposvertices[faces[i*3+1]].vertex=coshadowposvertices[faces[i*3]].vertex+Vector3(0.1,0,0);
			coshadowposvertices[faces[i*3+2]].vertex=coshadowposvertices[faces[i*3]].vertex+Vector3(0,0,0.1);
			coshadowposvertices[faces[i*3+1]+nVertices].vertex=coshadowposvertices[faces[i*3+1]].vertex;
			coshadowposvertices[faces[i*3+2]+nVertices].vertex=coshadowposvertices[faces[i*3+2]].vertex;
		}
		//v1.normalise();
		v1=v1/s;

		coshadownorvertices[faces[i*3]].normal+=v1;
		coshadownorvertices[faces[i*3+1]].normal+=v1;
		coshadownorvertices[faces[i*3+2]].normal+=v1;
	}
	//normalize
	for (i=0; i<nVertices; i++)
	{
		coshadownorvertices[i].normal.normalise();
		//texcoords
		coshadownorvertices[i].texcoord=covertices[i].texcoord;
	}

	return center;
}

Vector3 flexit()
{
	Vector3 center;
	if (smanager->getShadowTechnique()==SHADOWTYPE_STENCIL_MODULATIVE || smanager->getShadowTechnique()==SHADOWTYPE_STENCIL_ADDITIVE)
	{
		center=updateShadowVertices();
		//find the binding
		unsigned posbinding=msh->sharedVertexData->vertexDeclaration->findElementBySemantic(VES_POSITION)->getSource();
		HardwareVertexBufferSharedPtr pbuf=msh->sharedVertexData->vertexBufferBinding->getBuffer(posbinding);
		pbuf->lock(HardwareBuffer::HBL_DISCARD);
		pbuf->writeData(0, pbuf->getSizeInBytes(), shadowposvertices, true);
		pbuf->unlock();
		//find the binding
		unsigned norbinding=msh->sharedVertexData->vertexDeclaration->findElementBySemantic(VES_NORMAL)->getSource();
		HardwareVertexBufferSharedPtr nbuf=msh->sharedVertexData->vertexBufferBinding->getBuffer(norbinding);
		nbuf->lock(HardwareBuffer::HBL_DISCARD);
		nbuf->writeData(0, nbuf->getSizeInBytes(), shadownorvertices, true);
		nbuf->unlock();
		msh->getEdgeList()->updateFaceNormals(0, pbuf);

	}
		else
	{
		center=updateVertices();
		vbuf->lock(HardwareBuffer::HBL_DISCARD);
		vbuf->writeData(0, vbuf->getSizeInBytes(), vertices, true);
		vbuf->unlock();
		//msh->sharedVertexData->vertexBufferBinding->getBuffer(0)->writeData(0, vbuf->getSizeInBytes(), vertices, true);
	}
	return center;
}

};



#endif
