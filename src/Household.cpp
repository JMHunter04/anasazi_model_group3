#include "Household.h"
#include "repast_hpc/AgentId.h"
#include "repast_hpc/SharedContext.h"
#include "repast_hpc/SharedDiscreteSpace.h"
#include <stdio.h>
#include "repast_hpc/Random.h"

Household::Household(repast::AgentId id, int a, int deAge, int mStorage, float tFact)
{
	householdId = id;
	age = a;
	deathAge = deAge;
	maizeStorage = mStorage;
	assignedField = NULL;
	deathsWitnessed = 0;
	needs = 800; //hardcode rn, initialise only
	tensionFactor = tFact;
}

Household::~Household()
{

}

int Household::splitMaizeStored(int percentage)
{
	int maizeEndowment;
	maizeEndowment = maizeStorage * percentage;
	maizeStorage = maizeStorage - maizeEndowment;
	return maizeEndowment;
}

bool Household::checkMaize(float needs) //inefficiency in naming etc. needs can now be stored in this class
{
	if((assignedField->getExpectedYield() + maizeStorage) > needs)
	{
		return true;
	}
	else
	{
		return false;
	}
}

bool Household::death()
{
	if(age>=deathAge)
	{
			return true;
	}
	else
	{
		return false;
	}
}

bool Household::fission(int minFissionAge, int maxFissionAge, double gen, double fProb)
{
	if((age>=minFissionAge && age<=maxFissionAge) && (gen <= fProb))
	{
			return true;
	}
	else
	{
		return false;
	}
}

void Household::nextYear(float needs)
{
	age++;
	maizeStorage = assignedField->getExpectedYield() + maizeStorage - needs;
}

void Household::chooseField(Location* Field)
{
	//set the old location as emtpy
	if (assignedField!=NULL) assignedField->setState(0);

	//set the new location as a field
	Field->setState(2);

	assignedField = Field;
}

void Household::witnessDeath()
{
	if(deathsWitnessed <10){
		deathsWitnessed++;
	}
}

void Household::grieve()
{
	if(deathsWitnessed >0){
		deathsWitnessed--;
	}
}

float Household::calculateNeeds(int baseNeed) 
{
	float tension = deathsWitnessed * 0.1;
	needs = baseNeed + tension * tensionFactor * 0.1 * baseNeed;

	return needs;
}