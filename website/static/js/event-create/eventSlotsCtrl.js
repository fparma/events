/*global angular: false*/

angular.module('fpEvents.slots', [])
    .controller('slotsCtrl', ['$scope', '$http', '$timeout', 'FileUploadFactory', 'EventService',
            function ($scope, $http, $timeout, FileUploadFactory, EventService) {

            function resetSides() {
                $scope.sideSlots = {
                    west: [],
                    east: [],
                    guer: [],
                    civ: []
                };
            }
            resetSides();

            // helper array to keep the map ordered
            $scope.orderedSides = [
                {
                    getGroups: function () {
                        return $scope.sideSlots.west;
                    },
                    displayName: 'Blufor',
                    sideName: 'west'
                },
                {
                    getGroups: function () {
                        return $scope.sideSlots.east;
                    },
                    displayName: 'Opfor',
                    sideName: 'east'
                },
                {
                    getGroups: function () {
                        return $scope.sideSlots.guer;
                    },
                    displayName: 'Independent',
                    sideName: 'guer'
                },
                {
                    getGroups: function () {
                        return $scope.sideSlots.civ;
                    },
                    displayName: 'Civilian',
                    sideName: 'civ'
                },
            ];

            $scope.editManually = function () {
                resetSides();
                $scope.addNewGroup('west');
            };

            $scope.updateSideSelection = function (e, side) {
                var isAdd = e.target.checked;
                if (isAdd) {
                    $scope.addNewGroup(side);
                } else {
                    //remove
                    $scope.sideSlots[side] = [];
                }
            };

            $scope.anySideHaveUnits = function () {
                return ['west', 'east', 'guer', 'civ'].some($scope.sideHasUnits);
            };

            $scope.sideHasUnits = function (side) {
                var slotSide = $scope.sideSlots[side];
                for (var key in slotSide) {
                    var units = slotSide[key].units;
                    if (units && units.length > 0) {
                        return true;
                    }
                }
                return false;
            };

            $scope.addNewGroup = function (side, name) {
                $scope.sideSlots[side].push({
                    name: name || 'Group',
                    side: side,
                    units: [{}, {}, {}, {}, {}, {}, {}, {}]
                });
            };

            $scope.deleteGroup = function (side, idx) {
                $scope.sideSlots[side].splice(idx, 1);
            };

            $scope.addUnitToGroup = function (group) {
                return group.units.push({});
            };

            $scope.removeUnitFromGroup = function (group) {
                return group.units.splice(group.length - 1, 1);
            };

            $scope.uploadSQMFile = function () {
                var file = $scope.sqmFile;
                FileUploadFactory.getPlayableUnitsFromFile(file)
                    .then(function ok(data) {
                            $timeout(function () {
                                $scope.sideSlots = data;
                            }, 0);
                        },
                        function error(e) {
                            console.log(e);
                        });
            };

            $scope.checkValidAndSubmit = function () {
                var slots = {};
                for (var i in $scope.sideSlots) {
                    if ($scope.sideSlots[i].length) {
                        slots[i] = $scope.sideSlots[i];
                    }
                }
                var data = angular.toJson({
                    eventType: $scope.eventType.name,
                    eventImageUrl: $scope.eventImageUrl,
                    eventSlotsNumber: parseInt($scope.eventSlots, 10),
                    eventName: $scope.eventName,
                    eventNameFull: $scope.eventType.name + $scope.eventSlots + ' - ' + $scope.eventName,
                    eventDescription: $scope.eventDescription,
                    eventSlots: slots
                });
                
                EventService.createNewEvent(data);
            };
}]);