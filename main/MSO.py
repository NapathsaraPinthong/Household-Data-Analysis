import pandas as pd
from stellargraph import StellarGraph


class MSO():
    def load(self):
        household_ids = pd.read_excel('../data/dataset/node/household.xlsx', header=None)
        member_ids = pd.read_excel('../data/dataset/node/member.xlsx', header=None)
        income_ids = pd.read_excel('../data/dataset/node/income.xlsx', header=None)
        solid_ids = pd.read_excel('../data/dataset/node/solid.xlsx', header=None)
        disabled_ids = pd.read_excel('../data/dataset/node/disabled.xlsx', header=None)
        age_ids = pd.read_excel('../data/dataset/node/age.xlsx', header=None)
        prob_health_ids = pd.read_excel('../data/dataset/node/prob_health.xlsx', header=None)
        prob_family_ids = pd.read_excel('../data/dataset/node/prob_family.xlsx', header=None)

        member_hh_edges = pd.read_excel('../data/dataset/edge/mb-hh.xlsx', header=None, names=["source", "target"])
        hh_income_edges = pd.read_excel('../data/dataset/edge/hh-income_level.xlsx', header=None, names=["source", "target"])
        hh_solid_edges = pd.read_excel('../data/dataset/edge/hh-solid.xlsx', header=None, names=["source", "target"])
        member_disabled_edges = pd.read_excel('../data/dataset/edge/mb-disabled.xlsx', header=None, names=["source", "target"])
        member_age_edges = pd.read_excel('../data/dataset/edge/mb-age.xlsx', header=None, names=["source", "target"])
        member_prob_health_edges = pd.read_excel('../data/dataset/edge/mb-prob_health.xlsx', header=None, names=["source", "target"])
        member_prob_family_edges = pd.read_excel('../data/dataset/edge/mb-prob_family.xlsx', header=None, names=["source", "target"])

        # The dataset uses integers for node ids. However, the integers from 1 to 39 are used as IDs
        # for both users and groups. This is disambiguated by converting everything to strings and
        # prepending u to user IDs, g to group IDs, and c to community IDs.
        def hh(household):
            return "hh" + household.astype(str)

        def mb(member):
            return "mb" + member.astype(str)

        def inc(income):
            return "inc" + income.astype(str)

        def sl(solid):
            return "sl" + solid.astype(str)

        def dis(disabled):
            return "dis" + disabled.astype(str)

        def age(age):
            return "age" + age.astype(str)
        
        def ph(prob_health):
            return "ph" + prob_health.astype(str)
        
        def pf(prob_family):
            return "pf" + prob_family.astype(str)

        # nodes:
        household_ids = hh(household_ids)
        member_ids = mb(member_ids)
        income_ids = inc(income_ids)
        solid_ids = sl(solid_ids)
        disabled_ids = dis(disabled_ids)
        age_ids = age(age_ids)
        prob_health_ids = ph(prob_health_ids)
        prob_family_ids = pf(prob_family_ids)

        # node IDs in each edge:
        member_hh_edges["source"] = mb(member_hh_edges["source"])
        member_hh_edges["target"] = hh(member_hh_edges["target"])
        hh_income_edges["source"] = hh(hh_income_edges["source"])
        hh_income_edges["target"] = inc(hh_income_edges["target"])
        hh_solid_edges["source"] = hh(hh_solid_edges["source"])
        hh_solid_edges["target"] = sl(hh_solid_edges["target"])
        member_disabled_edges["source"] = mb(member_disabled_edges["source"])
        member_disabled_edges["target"] = dis(member_disabled_edges["target"])
        member_age_edges["source"] = mb(member_age_edges["source"])
        member_age_edges["target"] = age(member_age_edges["target"])
        member_prob_health_edges["source"] = mb(member_prob_health_edges["source"])
        member_prob_health_edges["target"] = ph(member_prob_health_edges["target"])
        member_prob_family_edges["source"] = mb(member_prob_family_edges["source"])
        member_prob_family_edges["target"] = pf(member_prob_family_edges["target"])

        # arrange the DataFrame indices appropriately: nodes use their node IDs, which have
        # been made distinct above, and the group edges have IDs after the other edges
        household_ids.set_index(0, inplace=True)
        member_ids.set_index(0, inplace=True)
        income_ids.set_index(0, inplace=True)
        solid_ids.set_index(0, inplace=True)
        disabled_ids.set_index(0, inplace=True)
        age_ids.set_index(0, inplace=True)
        prob_health_ids.set_index(0, inplace=True)
        prob_family_ids.set_index(0, inplace=True)


        start_hh_income_edges = len(member_hh_edges)
        hh_income_edges.index = range(start_hh_income_edges, start_hh_income_edges + len(hh_income_edges))
        start_hh_solid_edges = len(member_hh_edges) + len(hh_income_edges)
        hh_solid_edges.index = range(start_hh_solid_edges, start_hh_solid_edges + len(hh_solid_edges))
        start_member_disabled_edges = start_hh_solid_edges + len(hh_solid_edges)
        member_disabled_edges.index = range(start_member_disabled_edges, start_member_disabled_edges + len(member_disabled_edges))
        start_member_age_edges = start_member_disabled_edges + len(member_disabled_edges)
        member_age_edges.index = range(start_member_age_edges, start_member_age_edges + len(member_age_edges))
        start_member_prob_health_edges = start_member_age_edges + len(member_age_edges)
        member_prob_health_edges.index = range(start_member_prob_health_edges, start_member_prob_health_edges + len(member_prob_health_edges))
        start_member_prob_family_edges = start_member_prob_health_edges + len(member_prob_health_edges)
        member_prob_family_edges.index = range(start_member_prob_family_edges, start_member_prob_family_edges + len(member_prob_family_edges))

        return StellarGraph(
            nodes={"household": household_ids, "member": member_ids, "income": income_ids, "house_solid": solid_ids, "disabled": disabled_ids, "age": age_ids, "prob_health": prob_health_ids, "prob_family": prob_family_ids},
            edges={"belongs": member_hh_edges, "receives": hh_income_edges, "isSolid": hh_solid_edges, "isDisabled": member_disabled_edges, "age": member_age_edges, "have": member_prob_health_edges, "have": member_prob_family_edges},
        )