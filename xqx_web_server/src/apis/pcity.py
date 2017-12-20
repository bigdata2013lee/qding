#coding=utf8
from models.aptm import PCity, Project
from utils.tools import get_default_result


class PCityApi(object):

    def _get_ccity_ids(self, pid):
        """
        获取某省下的所有城市ID列表
        :param pid:
        :return:
        """
        ccity_ids = []
        p = PCity.objects(id=pid).first()
        if p:
            for ccity in p.childs:
                ccity_ids.append(ccity["_id"])

        return ccity_ids

    def list_pcitys(self):
        """
        列出所有有效的省-市信息
        :return: data ->  {collection:[{_id:"#s", name:"#s", childs:[...]}]}
        """

        result = get_default_result()
        pcitys = PCity.objects(is_valid=True)

        for pcity in pcitys:
            _pcity = pcity.to_mongo()
            _pcity['childs'] = [child for child in _pcity.get("childs", []) if child.get("is_valid", False)]
            result.data_collection.append(_pcity)

        return result

    def list_all_pcitys(self):
        """
        列出所有的省-市信息
        :return: data ->  {collection:[{_id:"#s", name:"#s", childs:[...]}]}
        """

        result = get_default_result()
        pcitys = PCity.objects()

        for pcity in pcitys:
            _pcity = pcity.to_mongo()
            _pcity['childs'] = [child for child in _pcity.get("childs", [])]
            result.data_collection.append(_pcity)

        return result

    def get_pcity(self, pid):
        """
        获取省市信息
        :param pid: T-string, 省ID
        :return:
        """
        result = get_default_result()
        result['data']['pcity'] = PCity.get_pcity(pid)

        return result

    def get_ccity(self, cid):
        """
        获取城市信息
        :param cid: T-string, 城市ID
        :return:
        """
        result = get_default_result()

        result['data']['city'] = PCity.get_ccity(cid)

        return result

    def set_ccity_valid(self, ccity_id, is_valid=True):
        """
        启用/禁用城市
        :param ccity_id:
        :param is_valid:
        :return:
        """
        result = get_default_result()
        pcity = PCity.objects(__raw__={"childs._id":ccity_id}).first()
        if not pcity:
            return result.setmsg("未找到城市信息", 3)

        p_is_valid = False
        for ccity in pcity.childs:
            if ccity["_id"] != ccity_id: continue
            ccity['is_valid'] = is_valid
            _valid = ccity.get("is_valid", False)
            p_is_valid = p_is_valid or _valid

        pcity.is_valid = p_is_valid
        pcity.save()
        return result

    def _tree_city_projects(self, projects_condition={}, rm_empty_node=True):
        result = get_default_result()
        pcitys = PCity.objects()

        for pcity in pcitys:
            _pcity = pcity.to_mongo()
            childs = _pcity.get("childs", []) or []
            _pcity['childs'] = childs

            __empty_projects_ccitys=[]
            for child in childs:
                projects = Project.objects(ccity_id=child.get("_id", ""), **projects_condition)
                child["projects"] = [project.outputEx(inculde_fields=["_id", "name", "label"]) for project in projects]

                if not child.get("projects", []): __empty_projects_ccitys.append(child)

            if rm_empty_node:
                for epc in __empty_projects_ccitys:
                    childs.remove(epc)

            if rm_empty_node and not childs:
                continue

            result.data_collection.append(_pcity)

        return result

    def tree_all_city_proejcts(self, rm_empty_node=True):
        """
        以树形结构组织省->市->项目
        :return: data->{collection:[...]}
        """
        return self._tree_city_projects(rm_empty_node=rm_empty_node)
