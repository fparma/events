/*global angular: false*/

angular.module('fpEvents')
    .directive('fileModel', ['$parse',
        function ($parse) {
            return {
                restrict: 'A',
                link: function (scope, element, attrs) {
                    var model = $parse(attrs.fileModel);
                    var modelSetter = model.assign;

                    element.bind('change', function () {
                        scope.$apply(function () {
                            modelSetter(scope, element[0].files[0]);
                        });
                    });
                }
            };
}]).directive('numbersOnly', function () {
        return {
            require: 'ngModel',
            restrict: 'A',
            link: function (scope, element, attrs, modelCtrl) {
                modelCtrl.$parsers.push(function (inputValue) {
                    if (inputValue === undefined) {
                        return '';
                    }
                    var transformedInput = Math.abs(inputValue.replace(/[^0-9+.]/g, '')) + '';
                    if (transformedInput.length > 2) {
                        transformedInput = (transformedInput[0] + transformedInput[1]);
                    }
                    if (transformedInput === '0') {
                        transformedInput = '';
                    }
                    if (transformedInput != inputValue) {
                        modelCtrl.$setViewValue(transformedInput);
                        modelCtrl.$render();
                    }

                    return transformedInput;
                });
            }
        };
    });